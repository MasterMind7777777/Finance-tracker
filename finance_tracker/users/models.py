from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True)
    currency = models.CharField(choices=settings.CURRENCIES.items(), default='USD', max_length=3)

    def __str__(self):
        return self.user.username
    
    @classmethod
    def get_or_create(cls, user):
        if user.userprofile:
            return user.userprofile
        else:
            return cls.objects.create(user=user)


class SocialMediaAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='socialmediaaccount')
    platform = models.CharField(max_length=50)
    username = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.platform}"


class PushNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}~{self.content}'


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def save(self, *args, **kwargs):
        if not self.pk:  # Only perform this validation for new objects
            existing_request = FriendRequest.objects.filter(from_user=self.to_user, to_user=self.from_user).exists()
            if existing_request:
                raise ValidationError('Friend request already exists for these users.')
        super().save(*args, **kwargs)

    def accept(self):
        self.accepted = True
        self.save()
        # Optionally, you can establish a friendship or perform additional actions here

    def decline(self):
        self.delete()
        # Optionally, you can perform additional actions here