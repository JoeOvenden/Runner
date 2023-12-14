from django import forms
from .models import *
from datetime import date

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profile_picture", "bio", "phone_number"]
        widgets = {
            "bio": forms.Textarea(attrs={"cols": 60, "rows": 10}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "date_time", "distance", "duration", 
                  "pace", "route"]
        widgets = {
            "description": forms.Textarea(attrs={"cols": 60, "rows": 6}),
            'date_time': forms.TextInput(attrs={'type':'datetime-local'}),
            "duration": forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            "pace": forms.TimeInput(attrs={'type': 'time'}, format='%M:%S')
        }
        labels = {
            "distance": "Distance (km)",
            "duration": "Duration (hh:mm)",
            "pace": "Pace per km",
            "date_time": "Date and time"
        }


class EventFilterForm(forms.Form):
    today = date.today()
    initial_end_date = today.replace(year=today.year + 1)
    start_date = forms.DateField(widget=forms.SelectDateWidget, initial=today)
    end_date = forms.DateField(widget=forms.SelectDateWidget, initial=initial_end_date)
    min_distance = forms.DecimalField(required=False)
    max_distance = forms.DecimalField(required=False)
    search_radius = forms.DecimalField(required=False, initial=2)
    coordinates = forms.CharField()

    def clean_min_distance(self):
        data = self.cleaned_data['min_distance']
        if data is not None and data < 0:
            raise forms.ValidationError("Please enter a non-negative number.")
        return data
    
    def clean_max_distance(self):
        data = self.cleaned_data['max_distance']
        # check max distance is non negative
        if data is not None and data < 0:
            raise forms.ValidationError("Please enter a non-negative number.")
        return data
    
    def clean_start_date(self):
        data = self.cleaned_data['start_date']
        # Check start date is not before today
        if data is not None and data < date.today():
            raise forms.ValidationError("Start date must be from today onwards.")
        return data 
    
    def clean_end_date(self):
        data = self.cleaned_data['end_date']
        # Check start date is not before today
        if data is not None and data < date.today():
            raise forms.ValidationError("End date must be from today onwards.")
        return data 
    
    def clean_coordinates(self):
        data = self.cleaned_data['coordinates']
        # Check that coordinates are in the format lat,lng
        data = data.split(",")
        print(data)
        if len(data) != 2:
            raise forms.ValidationError("Coordinates must be in the form: lat,lng")
        else:
            try:
                x = float(data[0])
                x = float(data[1])
            except ValueError:
                raise forms.ValidationError("Coordinates must be in the form: lat,lng")
        return data
    

class FilterProfileEventsForm(forms.Form):
    WHEN_OPTIONS = (
        ("upcoming", "Upcoming"),
        ("past", "Past")
    )
    STATUS_OPTIONS = (
        ("attending", "Attending"),
        ("organised", "Organised")
    )
    # LHS in sorting_options correspond to Event model field names. 
    # "-" is a prefix used to reverse ordering when using "Q.sort_by()"
    SORTING_OPTIONS = (
        ("date_time", "Newest to oldest"),
        ("-date_time", "Oldest to newest"),
        ("distance", "Sort by distance (ascending)"),
        ("-distance", "Sort by distance (descending)")
    )
    when = forms.ChoiceField(choices=WHEN_OPTIONS, initial='upcoming', label="")
    status = forms.ChoiceField(choices=STATUS_OPTIONS, initial='attending', label="")
    sorting = forms.ChoiceField(choices=SORTING_OPTIONS, initial='date_time', label="")