from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "profile_picture", "bio")

class FollowAdmin(admin.ModelAdmin):
    list_display = ("user_following", "user_followed")

class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organiser", "date_time", "description")

class EventAttendenceAdmin(admin.ModelAdmin):
    list_display = ("event", "user")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "text")


class LikeAdmin(admin.ModelAdmin):
    list_display = ("comment", "user")



# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Event_Attendence, EventAttendenceAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)