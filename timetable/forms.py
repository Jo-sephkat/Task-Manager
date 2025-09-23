from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Subject, Class

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['day', 'start_time', 'end_time', 'location', 'instructor']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'time-input'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'time-input'}),
            'day': forms.Select(attrs={'class': 'day-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data
    
    
    