import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.conf import settings
from decimal import Decimal
from geopy.distance import geodesic
from django.db.models import Q

import datetime


from .models import *
from .forms import *

import os

def list_files_in_directory(directory_path):
    file_list = []

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)

        # Check if it's a regular file
        if os.path.isfile(filepath):
            file_list.append(filepath)
    
    return file_list


def get_events_attended(user, reverse=False, start_date=None, end_date=None):
    event_attendence_objects = user.events_attending.all()
    events_attending = event_attendence_objects.values("event")
    events_attending = Event.objects.filter(pk__in=events_attending).order_by('date_time')
    if start_date is not None:
        events_attending = events_attending.filter(date_time__gte=start_date)
    if end_date is not None:
        events_attending = events_attending.filter(date_time__lte=end_date)
    return events_attending


def get_event_datetime(event):
    event_datetime = datetime.datetime.combine(event.date, event.time)
    return event_datetime


def index(request):
    events = []
    if not request.user.is_anonymous:
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=7)
        events = get_events_attended(request.user, start_date=start_date, end_date=end_date)
    return render(request, "runner/index.html", {
        "events": events,
    })


@csrf_exempt
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("runner:index"))
        else:
            return render(request, "runner/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "runner/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("runner:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "runner/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "runner/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("runner:index"))
    else:
        return render(request, "runner/register.html")


def profile(request, username):
    def display(form=FilterProfileEventsForm()):
        try:
            user = User.objects.get(username=username)
        
        except User.DoesNotExist:
            return redirect('404')

        if request.user.is_anonymous or not user.followers.filter(user_following=request.user).exists():
            is_following = False
        else:
            is_following = True

        try:
            status = form.cleaned_data['status']
            when = form.cleaned_data['when']
            sorting = form.cleaned_data['sorting']
        except AttributeError:
            status = form.fields['status'].initial
            when = form.fields['when'].initial
            sorting = form.fields['sorting'].initial
        except KeyError:
            return HttpResponse(400)

        if status == "organised":                   # If getting events organised
            events = user.events_organised.all()    # Get events
        else:                                       # Otherwise getting events attended
            events = get_events_attended(user)      # Get events

        if when == "upcoming":                      # If getting upcoming events
            events = Event.objects.filter(pk__in=events).filter(date_time__gte=datetime.datetime.now())
        elif when == "past":                        # If getting past events
            events = Event.objects.filter(pk__in=events).filter(date_time__lt=datetime.datetime.now())

        events = events.order_by(sorting)
        events, page = paginate(request, events, 25)

        data = {
            "profile": user,
            "follower_count": user.follower_count,
            "following_count": user.following_count,
            "is_following": is_following,
            "events": events,
            "page": page,
            "status": status,
            "when": when,
            "form": form,
        }
        return render(request, "runner/profile.html", data)
    

    if request.method == "POST":
        # Note: if the form is invalid, returning display is still the intended course of action.
        # Calling form.is_valid() ensures that form.cleaned_data is available.
        form = FilterProfileEventsForm(request.POST)
        if not form.is_valid():
            print("INVALID_FORM")
        return display(form=form)

    elif request.method == "GET":
        return display()


def paginate(request, items, count_per_page):
    p = Paginator(items, count_per_page)        # Create paginator object

    page_number = 1
    if 'page' in request.GET:
        try:
            page_number = int(request.GET['page'])
        except ValueError:
            pass

    # If getting posts for a page that doesn't exist
    if page_number > p.num_pages or page_number < 1:
        return None, p.page(1)

    page = p.page(page_number)      # Get the page object
    page_items = page.object_list

    return page_items, page


@login_required
def edit_profile(request):
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect(f'profile/{request.user}')
    else:
        form = ProfileForm(instance=user)
    return render(request, "runner/edit_profile.html", {"form": form})


@csrf_exempt
@login_required
def edit_avatar(request):
    if request.method == "GET":
        # Get avatar components for user to choose from
        components_path = "media/avatars/components/"
        eyes = list_files_in_directory(components_path + "eyes/")
        mouths = list_files_in_directory(components_path + "mouths/")
        
        # Return template with components
        return render(request, "runner/edit_avatar.html", {
            "eyes": eyes,
            "mouths": mouths
        })
    
    elif request.method == "PUT":
        data = json.loads(request.body)
        request.user.avatar_eyes = data["filenames"]["eyes"]
        request.user.avatar_mouth = data["filenames"]["mouth"]
        request.user.avatar_colour = data["colour"]
        request.user.save()
        return HttpResponse(200)


@csrf_exempt
@login_required
def follow(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        profile = data.get("profile_username")

        # Make sure the user to be followed exists
        if User.objects.filter(username=profile).exists() is False:
            return HttpResponse(400)    # Bad request
        
        # Make sure user is not trying to follow themselves
        profile_user = User.objects.get(username=profile)
        user = User.objects.get(username=request.user)
        if profile_user == request.user:
            return HttpResponse(400)    # Bad request
        
        # If following already exists then delete it
        try:
            following = profile_user.followers.get(user_following=request.user)
            following.delete()
            change = -1

        # Otherwise create the following
        except Follow.DoesNotExist:
            following = Follow(user_following=request.user, user_followed=profile_user)
            following.save()
            change = 1

        # Change the number of followers for the profile user and followings for the current user
        profile_user.follower_count += change
        user.following_count += change
        profile_user.save()
        user.save()
        return JsonResponse({'change': change})

        
@csrf_exempt
@login_required
def attend(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        event_id = data.get("event_id")

        # Make sure the user to be attended exists
        if Event.objects.filter(id=event_id).exists() is False:
            return HttpResponse(400)    # Bad request
        
        event = Event.objects.get(id=event_id)
        user = User.objects.get(username=request.user)

        # # Make sure user is not trying to attend/unattend their own event
        # if event.organiser == request.user:
        #     return HttpResponse(400)    # Bad request
        
        # If attendence already exists then delete it
        try:
            attending = event.attendence.get(user=user)
            attending.delete()
            change = -1

        # Otherwise create the following
        except Event_Attendence.DoesNotExist:
            attending = Event_Attendence(user=request.user, event=event)
            attending.save()
            change = 1


        # Change the number of people attending the event
        return JsonResponse({'change': change})


def get_rating_value(post, user):
    # If user is not logged in then just return 0
    if user.is_anonymous:
        return 0

    # Returns how the user rated the post as -1/0/1. 0 indicates the user has not rated the post
    try:
        rating = post.ratings.get(user=user)
        return rating.rating

    except Rating.DoesNotExist:
        return 0


def get_stats(events):
    km_total = sum(event.distance for event in events)
    number_of_runs = len(events)
    return [
        {"label": "Total Kilometers", "value": km_total},
        {"label": "Longest Run", "value": max(event.distance for event in events)},
        {"label": "Number of Runs", "value": number_of_runs},
        {"label": "Average Distance", "value": round(km_total / number_of_runs, 1)},
    ]


def celebrate(request, username):
    """
    A page devoted to celebrating a user's runs and statistics.
    """
    # Get the user's previous events attended
    # Add up the stats!
    events_attended = get_events_attended(request.user, end_date=datetime.datetime.now())
    return render(request, "runner/celebrate.html", {
        "stats": get_stats(events_attended),
    })


def filter_users_by_username(request, profiles=User.objects.all()):
    # Optionally takes profiles to filter or otherwise uses all users and then filters by the user search
    # If there is not user search then returns all profiles
    if "user_search" in request.GET:
        user_search = request.GET["user_search"]
        profiles = profiles.filter(username__icontains=user_search)
    return profiles


def user_search(request):
    if request.method == "GET":
        profiles = filter_users_by_username(request)

        profiles, page = paginate(request, profiles, 25)

        return render(request, "runner/user-search.html", {
            "profiles": profiles,
            "page": page,
        })


def create_event(request):
    # If user has created a new event
    if request.method == "POST":

        # Make a new event object, and then load the form information into a profile form
        # with the event linked to it
        event = Event()
        form = EventForm(request.POST, instance=event)

        # Check if the form is invalid and if so return the form with an error message
        if not form.is_valid():
            return render(request, "runner/create_event.html", {
                "form": form
        })
    
        event.description = form.cleaned_data["description"]
        event.organiser = request.user
        event.date_time = form.cleaned_data["date_time"]

        # If user has uploaded a gpx file
        if request.POST["uploadMethod"] == "gpx":
            event.route = request.FILES["route"]
    
        event.start_point_lat = Decimal(request.POST["startLatitude"]).quantize(Decimal('0.00000'))
        event.start_point_lng = Decimal(request.POST["startLongitude"]).quantize(Decimal('0.00000'))
        event.end_point_lat = Decimal(request.POST["endLatitude"]).quantize(Decimal('0.00000'))
        event.end_point_lng = Decimal(request.POST["endLongitude"]).quantize(Decimal('0.00000'))

        

        event.save()

        # Create event attendence for organiser, since the organiser should really attend!
        attendence = Event_Attendence()
        attendence.event = event
        attendence.user = request.user
        attendence.save()

        # Redirect user to the new event page
        return redirect(f'event/{event.id}')


    form = EventForm()
    return render(request, "runner/create_event.html", {
        "form": form
    })


def get_rating_value(comment, user):
    # Returns 1 if the user has liked the comment and 0 otherwise
    return int(comment.likes.filter(user=user).exists())
    

@login_required(login_url='runner:login')
def like_comment(request):
    if request.method == "POST":
        comment_id = json.loads(request.body)

        # Get post
        comment = Comment.objects.get(id=comment_id)
        post_like_change = 1                      # How much the post rating changes by

        # If the comment is already liked by the user, then they are removing their like
        try:    
            like_object = comment.likes.get(user=request.user)  # Get the like object
            like_object.delete()                                # Delete the like object
            post_like_change = -1                               # Remember that the like count for the post is decreasing by 1

        # If the comment has not yet been liked by the user
        except Like.DoesNotExist:
            like_object = Like(comment=comment, user=request.user)  # Create a new like object
            like_object.save()                                      # Save it
            post_like_change = 1                                    # Remember that the like count for the post is increasing by 1
            
        # Update comment rating
        comment.like_count += post_like_change
        comment.save()
        return JsonResponse({'new_rating': comment.like_count})


@login_required(login_url='runner:login')
def event_page(request, event_id):

    try:
        event = Event.objects.get(id = event_id)
    except Event.DoesNotExist:
        return redirect('404')

    def display(form=CommentForm()):
        users_attending = [attending.user for attending in event.attendence.all()]
        number_of_attending = len(users_attending)
        comments = event.comments.all()

        # Get dictionary where the keys are comments and the values are the booleans representing if the user has liked the comment
        comment_user_likes_dict  = {comment: get_rating_value(comment, request.user) for comment in comments}


        return render(request, "runner/event.html", {
            "event": event,
            "number_of_attending": number_of_attending,
            "attending": users_attending,
            "is_going": request.user in users_attending,
            "form": form,
            "comment_user_likes_dict": comment_user_likes_dict,
        })
        

    if request.method == "GET":
        return display()
    
    if request.method == "POST":
        form = CommentForm(request.POST)

        if not form.is_valid():
            return display(form)
        
        comment = Comment()
        comment.user = request.user
        comment.event = event
        comment.text = form.cleaned_data["text"]
        comment.save()
        return display()


def page_not_found(request):
    return render(request, "runner/404.html")


def get_events(start_date=None, end_date=None, min_distance=None, max_distance=None, 
               title_filter=None):
    """"
    Returns events from today onwards with optional filters for:
        dates from start_date
        dates before or on end_date
        minimum distance
        maximum distance
        title partial

    Events are returned as a list sorted in chronological order
    """
    events = Event.objects.filter(date_time__gte=datetime.date.today())

    if start_date is not None:
        events = events.filter(date_time__gte=start_date)

    if end_date is not None:
        events = events.filter(date_time__lte=end_date)

    if min_distance is not None:
        events = events.filter(distance__gte=min_distance)
    
    if max_distance is not None:
        events = events.filter(distance__lte=max_distance)

    if title_filter is not None:
        events = events.filter(title__icontains=title_filter)

    events = sorted(events, key=lambda event : event.date_time)
    return events


def radius_filter(events, latlng, radius):
    def distance(event):    # Return distance in km from event to marked location (latlng)
        return geodesic(latlng, (event.start_point_lat, event.start_point_lng)).kilometers
    events = list(filter(lambda event: distance(event) <= radius, events))
    return events


def events_search(request):
    def display(events=Event.objects.none(), form=EventFilterForm()):
        events, page = paginate(request, events, 25)

        return render(request, "runner/events_search.html", {
            "form": form,
            "events": events,
            "page": page
        })
    
    if len(request.GET) != 0:
        filter_form = EventFilterForm(request.GET)
        
        # If the form is not valid then return page back to them with the form
        if not filter_form.is_valid():
            return display(form=filter_form)
        
        start_date = filter_form.cleaned_data["start_date"]
        end_date = filter_form.cleaned_data["end_date"]
        min_distance = filter_form.cleaned_data["min_distance"]
        max_distance = filter_form.cleaned_data["max_distance"]
        title_filter = request.GET["user_search"]

        # Get all events between the start and end date filters
        events = get_events(start_date=start_date, end_date=end_date, min_distance=min_distance, 
                            max_distance=max_distance, title_filter=title_filter)
        
        latlng_str = filter_form.cleaned_data["coordinates"]
        search_radius = filter_form.cleaned_data["search_radius"]
        try:
            latlng = [float(x) for x in latlng_str]
            search_radius = float(search_radius)
            events = radius_filter(events, latlng, search_radius)
        except ValueError:
            print("Error: Radius or coordinates value error.")

        return display(events=events, form=filter_form)
    
    else:
        # Display page
        return display()
    
    
@login_required(login_url="runner:login")
def follow_page(request, follow_type):
    # Page showing accounts that are being followed by the user or accounts that are following
    # the user depending on follow_type
    if follow_type == "following":
        follow_objects = request.user.followings.all()
        profiles = User.objects.filter(followers__in=follow_objects)

    elif follow_type == "followers":
        follow_objects = request.user.followers.all()
        profiles = User.objects.filter(followings__in=follow_objects)


    profiles = filter_users_by_username(request, profiles)
    profiles, page = paginate(request, profiles, 3)

    return render(request, "runner/follow_page.html", {
        "profiles": profiles,
        "page": page,
        "follow_type": follow_type,
    })


def following(request):
    return follow_page(request, "following")


def followers(request):
    return follow_page(request, "followers")

