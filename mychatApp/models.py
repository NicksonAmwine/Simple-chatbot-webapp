from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, AbstractUser
from PIL import Image
import os
from django.core.files import File
from django.core.files.storage import default_storage
from django.db.models.signals import post_save
from django.dispatch import receiver
 
NewUser = get_user_model()

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()
     

    def __str__(self):
        return self.user.username
    
    # resizing images
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Check if the new image file exists
        if default_storage.exists(self.avatar.path):
            img = Image.open(self.avatar.path)
            if img.height > 100 or img.width > 100:
                output_size = (100, 100)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
        else:
            default_image_path = os.path.join(default_storage.location, 'profile_images', 'default.jpg')
            if default_storage.exists(default_image_path):
                self.avatar.save('default.jpg', File(open(default_image_path, 'rb')))
            else:
                print("Default image not found. Please make sure 'default.jpg' exists in the 'profile_images' directory.")

        if self.pk:  # if the instance already exists in the database
            old_image = Profile.objects.get(pk=self.pk).avatar
            if old_image != self.avatar and old_image.name != 'default.jpg':  # if the image has changed
                old_image.delete(save=False)  # delete the old image file

class OTP(models.Model):
    user = models.OneToOneField(NewUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

# Signal handlers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # timestamp = models.DateTime
# Create your models here.
