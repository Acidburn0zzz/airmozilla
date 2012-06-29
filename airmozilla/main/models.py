import datetime
import hashlib
import os

from django.db import models


def _upload_path(instance, filename):
    now = datetime.datetime.now()
    path = now.strftime('%Y/%m/%d/')
    hashed_filename = hashlib.md5(filename + str(now.microsecond)).hexdigest()
    __, extension = os.path.splitext(filename)
    return path + hashed_filename + extension


class Participant(models.Model):
    """ Participants - speakers at events. """
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True)
    photo = models.FileField(upload_to=_upload_path, blank=True)
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

    def __unicode__(self):
        return self.name


class Category(models.Model):
    """ Categories globally divide events - one category per event. """
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    """ Tags are flexible; events can have multiple tags. """
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Event(models.Model):
    """ Events - all the essential data and metadata for publishing. """
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, max_length=200)
    video_url = models.URLField(blank=True)
    STATUS_CHOICES = (
        ('I', 'Initiated'),
        ('S', 'Scheduled')
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES,
                              default='I')
    placeholder_img = models.FileField(upload_to=_upload_path)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(
                      help_text='Enter times in the US Pacific timezone.')
    participants = models.ManyToManyField(Participant,
                          help_text='Speakers or presenters for this event.')
    location = models.CharField(max_length=50)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    call_info = models.TextField(blank=True)
    additional_links = models.TextField(blank=True)
    public = models.BooleanField(default=False,
                    help_text='Available to everyone (else MoCo only.)')
    featured = models.BooleanField(default=False)
