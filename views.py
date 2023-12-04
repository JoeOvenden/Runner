import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from decimal import Decimal
from geopy.distance import geodesic
import datetime

from .models import *
from .forms import *

def index(request):
    return render(request, "runner/index.html")

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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "runner/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "runner/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "runner/register.html")


def profile(request, username):
    try:
        user = User.objects.get(username=username)
    
    except User.DoesNotExist:
        return redirect('404')

    if request.user.is_anonymous or not user.followers.filter(user_following=request.user).exists():
        is_following = False
    else:
        is_following = True

    # Get all the people that the user follows
    follow_objects = user.followings.all()  # Follow objects where user is the follower
    user_follows = [follow_object.user_followed for follow_object in follow_objects]
    
    # Get all the users events
    events = user.events_organised.all()

    data = {
        "profile": user,
        "follower_count": user.follower_count,
        "following_count": user.following_count,
        "is_following": is_following,
        "events": events
    }
    data.update(paginate(user_follows, 6, "user_follows"))

    return render(request, "runner/profile.html", data)


def paginate(items, count_per_page, items_label):
    """
    Takes set of posts and returns a dictionary with 2 entries
    
    posts_user_ratings_dict is a dictionary of posts together with how the user has rated each post
    page_obj is a paginator page object that has information about whether or not there is a next or previous page

    Data for at most n posts is returned (by default 10), and which posts are based on the get parameter 'page'
    which determines which page is being looked at
    """


    # Sort posts in reverse chronological order and then make a paginator with n posts per page
    # items = sorted(posts, key=lambda post : post.timestamp, reverse=True)
    p = Paginator(items, count_per_page)

    # Get the page number
    page_number = 1
    """
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1
    """

    # If getting posts for a page that doesn't exist
    if page_number > p.num_pages or page_number < 1:
        return None

    page = p.page(page_number)      # Get the page object
    page_items = page.object_list

    return {
        items_label: page_items,
        "page_obj": page
    }


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

        print(change)

        # Change the number of people attending the event
        return JsonResponse({'change': change})


@login_required(login_url='/login')
def following_page(request):
    followings = request.user.followings.all()                                  # Get all the following objects of the user
    users_followed = [following.user_followed for following in followings]      # Get all the user objects of the users followed
    posts = Post.objects.filter(user__in=users_followed)                        # Get all the posts from the users followed
    return render(request, "network/following.html", get_posts_data(request, posts))


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


def celebrate(request, username):
    return render(request, "runner/celebrate.html")


def user_search(request):
    print(request.method)
    if request.method == "POST":
        try:
            user_search = request.POST["user_search"]
        except KeyError:
            return render(request, "runner/user-search.html")
        
        profiles = User.objects.filter(username__icontains=user_search)

    elif request.method == "GET":
        profiles = User.objects.all()

    return render(request, "runner/user-search.html", {
        "profiles": profiles
    })


def create_event(request):
    # If user has created a new event
    if request.method == "POST":

        # Make a new event object, and then load the form information into a profile form
        # with the event linked to it
        event = Event()
        form = EventForm(request.POST, request.FILES, instance=event)

        # Check if the form is invalid and if so return the form with an error message
        if not form.is_valid():
            return render(request, "runner/create_event.html", {
                "form": form
        })
    
        event.date = form.cleaned_data["date"]
        event.time = form.cleaned_data["time"]
        event.description = form.cleaned_data["description"]
        event.organiser = request.user

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


def event_page(request, event_id):
    try:
        event = Event.objects.get(id = event_id)
    except Event.DoesNotExist:
        return redirect('404')
    
    users_attending = [attending.user.username for attending in event.attendence.all()]
    return render(request, "runner/event.html", {
        "event": event,
        "attending": users_attending,
        "is_going": request.user.username in users_attending
    })



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
    events = Event.objects.filter(date__gte=datetime.date.today())

    if start_date is not None:
        events = events.filter(date__gte=start_date)

    if end_date is not None:
        events = events.filter(date__lte=end_date)

    if min_distance is not None:
        events = events.filter(distance__gte=min_distance)
    
    if max_distance is not None:
        events = events.filter(distance__lte=max_distance)

    if title_filter is not None:
        events = events.filter(title__icontains=title_filter)

    events = sorted(events, key=lambda e : e.date)
    return events


def radius_filter(events, latlng, radius):
    def distance(event):    # Return distance in km from event to marked location (latlng)
        return geodesic(latlng, (event.start_point_lat, event.start_point_lng)).kilometers
    events = list(filter(lambda event: distance(event) <= radius, events))
    return events

def events_search(request):
    def display(events=None, form=EventFilterForm()):
        return render(request, "runner/events_search.html", {
            "form": form,
            "events": events
        })
    
    if request.method == "POST":
        filter_form = EventFilterForm(request.POST)
        
        # If the form is not valid then return page back to them with the form
        if not filter_form.is_valid():
            return display(form=filter_form)
        
        start_date = filter_form.cleaned_data["start_date"]
        end_date = filter_form.cleaned_data["end_date"]
        min_distance = filter_form.cleaned_data["min_distance"]
        max_distance = filter_form.cleaned_data["max_distance"]
        title_filter = request.POST["user_search"]

        # Get all events between the start and end date filters
        events = get_events(start_date=start_date, end_date=end_date, min_distance=min_distance, 
                            max_distance=max_distance, title_filter=title_filter)
        
        latlng_str = filter_form.cleaned_data["coordinates"]
        print(latlng_str)
        search_radius = filter_form.cleaned_data["search_radius"]
        try:
            latlng = [float(x) for x in latlng_str]
            search_radius = float(search_radius)
            events = radius_filter(events, latlng, search_radius)
        except ValueError:
            print("Error: Radius or coordinates value error.")

        return display(events=events, form=filter_form)

    # Display page
    return display()