from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class NutritionProgram(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='nutrition_programs/')
    proteins = models.DecimalField(max_digits=5, decimal_places=2)
    fats = models.DecimalField(max_digits=5, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2)
    kcal = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.title


class WorkoutProgram(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='workout_programs/')
    description = models.TextField()

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_recipes = models.ManyToManyField('NutritionProgram', related_name='saved_by', blank=True)
    saved_workouts = models.ManyToManyField('WorkoutProgram', related_name='saved_by', blank=True)

    def __str__(self):
        return self.user.username


class NotificationNew(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    image = models.ImageField(upload_to='notifications/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    role=models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.timestamp}'



class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"


class Avatar(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='avatar',
        verbose_name=_('User')
    )
    image = models.ImageField(
        upload_to='avatars/',
        default='avatars/profile picture.png',
        verbose_name=_('Image')
    )

    class Meta:
        verbose_name = _('Avatar')
        verbose_name_plural = _('Avatars')

    def __str__(self):
        return f"{self.user.username}'s avatar"


class Blogs(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='blogs/')
    description = models.TextField()

    def __str__(self):
        return self.title


class RegistrationForm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registration_form')
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    height = models.IntegerField()
    weight = models.IntegerField()
    daily_activity = models.IntegerField()

    def __str__(self):
        return f"Registration data for {self.user.username}"
