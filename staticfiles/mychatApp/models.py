from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, AbstractUser
from PIL import Image
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
        if self.pk:  # if the instance already exists in the database
            old_image = Profile.objects.get(pk=self.pk).avatar
            if old_image != self.avatar and old_image.name != 'default.jpg':  # if the image has changed
                old_image.delete(save=False)  # delete the old image file
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)

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

# Create your models here.
