from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "profile_picture", "bio")

class FollowAdmin(admin.ModelAdmin):
    list_display = ("user_following", "user_followed")

class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organiser", "date", "time", "description")

class EventAttendenceAdmin(admin.ModelAdmin):
    list_display = ("event", "user")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Event_Attendence, EventAttendenceAdmin)