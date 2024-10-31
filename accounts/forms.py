from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import TranscendenceUser

class TranscendenceUserCreationForm(UserCreationForm):
    display_name = forms.CharField(max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = TranscendenceUser
        fields = ('username', 'email', 'display_name')

class TranscendenceUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = TranscendenceUser
        fields = ('email', 'display_name', 'avatar')