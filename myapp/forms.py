import re
from django import forms
from django.contrib.auth.forms import UserCreationForm,  UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Avatar

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = Avatar
        fields = ['image']
