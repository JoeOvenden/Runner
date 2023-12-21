from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
import datetime


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True)
    use_avatar = models.BooleanField(default=True)
    avatar_mouth = models.CharField(max_length=100, default="open_wide.svg")
    avatar_eyes = models.CharField(max_length=100, default="smooth_shocked.svg")
    avatar_colour = models.CharField(max_length=7, default="#FFFF00")
    bio = models.CharField(max_length=800, blank=True)
    phone_number = PhoneNumberField(blank=True)
    account_creation_date = models.DateField(auto_now_add=True)
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    total_km_run = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    """
    Total Km run
    Longest distance
    """

    def avatar(self):
        return {
            "mouth": self.avatar_mouth,
            "eyes": self.avatar_eyes,
            "colour": self.avatar_colour
        }


class Follow(models.Model):
    user_following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followings")
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")


class Event(models.Model):
    organiser = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="events_organised", null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_time = models.DateTimeField(default=timezone.now)
    duration = models.TimeField()
    distance = models.DecimalField(max_digits=7, decimal_places=1)
    pace = models.TimeField(default=datetime.time(0, 6))
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=400)
    start_point_lat = models.DecimalField(max_digits=10, decimal_places=5)
    start_point_lng = models.DecimalField(max_digits=10, decimal_places=5)
    end_point_lat = models.DecimalField(max_digits=10, decimal_places=5)
    end_point_lng = models.DecimalField(max_digits=10, decimal_places=5)
    route = models.FileField(upload_to='gpx_files', blank=True)

    def __str__(self):
        return f"{self.date_time.date().strftime('%d-%m-%Y')}: {self.title}"

    def formatted_duration(self):
        text = ""
        if self.duration.hour:
            text += str(self.duration.hour) + " hour"
            if self.duration.hour != 1:
                text += "s"
        
        if self.duration.minute:
            text += f" {self.duration.minute} minute"
            if self.duration.minute  != 1:
                text += "s"
        return text
    
    def formatted_pace(self):
        return "{:02d}:{:02d} per km".format(self.pace.hour, self.pace.minute)
    
    def formatted_distance(self):
        if self.distance % 1 == 0:
            formatted_distance = "{:.0f} km".format(self.distance)
        else:
            formatted_distance = "{:.1f} km".format(self.distance)

        if self.distance != 1:
            formatted_distance += "s"
        return formatted_distance
    
    def formatted_time(self):
        return self.date_time.strftime("%I:%M%p").lower()


class Event_Attendence(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendence")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events_attending")


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="comments", null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=400)
    timestamp = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField(default=0)


class Like(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")          # The user the likes the comment

