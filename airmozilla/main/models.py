from django.db import models
from django.contrib.auth.models import User


class Participant(models.Model):
    """ Participants - speakers at events. """
    name = models.CharField(max_length=50)
    photo = models.FileField(upload_to='participants/')
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=50, blank=True)
    team = models.CharField(max_length=50, blank=True)
    irc = models.CharField(max_length=50, blank=True)
    topic_url = models.URLField(blank=True)
    blog_url = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    ROLE_CHOICES = (
        ('C', 'Event Coordinator'),
        ('PP', 'Principal Presenter'),
        ('P', 'Presenter'),
    )
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)
    CLEARED_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('F', 'Final Cut'),
    )
    cleared = models.CharField(max_length=2,
                               choices=CLEARED_CHOICES, default='N')


class Category(models.Model):
    """ Categories globally divide events - one category per event. """
    name = models.CharField(max_length=50)


class Tag(models.Model):
    """ Tags are flexible; events can have multiple tags. """
    name = models.CharField(max_length=50)


class Event(models.Model):
    """ Events - all the essential data and metadata for publishing. """
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True)
    placeholder_img = models.FileField(upload_to='placeholders/')
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(Participant)
    location = models.CharField(max_length=50)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    call_info = models.TextField(blank=True)
    additional_links = models.TextField(blank=True)
    public = models.BooleanField(default=False)
