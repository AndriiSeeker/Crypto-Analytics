from cloudinary.forms import CloudinaryFileField
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.URLField(null=True, max_length=300)
    bio = models.CharField(default=None, null=True, max_length=500)

    def __str__(self):
        return str(self.avatar)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorites = ArrayField(models.IntegerField(max_length=10, null=True), blank=True, default=list)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Watchlist.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()