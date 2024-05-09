from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NutritionProgram, WorkoutProgram, NotificationNew, Avatar
from django.contrib.auth.models import User
from django.conf import settings

@receiver(post_save, sender=NutritionProgram)
def create_recipe_notification(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.all():
            NotificationNew.objects.create(
                user=user,
                title='Новый рецепт',
                message=f'Попробуйте новый рецепт: {instance.title}',
                image=instance.image
            )

@receiver(post_save, sender=WorkoutProgram)
def create_workout_notification(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.all():
            NotificationNew.objects.create(
                user=user,
                title='Новая тренировка',
                message=f'Попробуйте новую тренировку: {instance.title}',
                image=instance.image
            )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_avatar(sender, instance, created, **kwargs):
    if created:
        Avatar.objects.create(user=instance)
    else:
        instance.avatar.save()