from django.db import models
from django.contrib.auth.models import AbstractUser

# from django.contrib.postgres.fields import ArrayField, JSONField

# Create your models here.

class Bird(models.Model):
    GROUPS = ( ('EE', 'Eastern Empids'),)

    class Meta:
        unique_together = ('group', 'seq')

    asset_id = models.IntegerField(unique=True, db_index=True)

    # ebird_image_data = JSONField()

    species_code = models.CharField(max_length=6)
    group = models.CharField(max_length=6, choices=GROUPS)
    seq = models.PositiveIntegerField(unique=True, db_index=True)

    common_name = models.CharField(max_length=200)
    image_url = models.URLField()

    location_line1 = models.TextField()
    location_line2 = models.TextField()
    observation_date = models.DateField()
    ebird_user_id = models.TextField()
    ebird_rating = models.FloatField()
    ebird_user_display_name  = models.TextField()
    ebird_checklist_id = models.TextField()
    image_width = models.PositiveIntegerField(null=True, blank=True) 
    image_height = models.PositiveIntegerField(null=True, blank=True) 

    location = models.TextField()

    is_active = models.BooleanField(default=True)
    deactivated_on = models.DateTimeField(null=True, blank=True)
    deactivated_by = models.ForeignKey('core.User', on_delete=models.CASCADE, null=True, blank=True)


class User(AbstractUser):
    pass


class Guess(models.Model):
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    species_code = models.CharField(max_length=6, help_text="Guessed species code.")
    confidence = models.PositiveSmallIntegerField(default=0)

    is_correct = models.BooleanField()

    created = models.DateTimeField(auto_now_add=True)
