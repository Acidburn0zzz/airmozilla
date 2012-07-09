import datetime
import hashlib
import os

from django.conf import settings
from django.db import models
from django.utils.timezone import utc


def _upload_path(tag):
    def _upload_path_tagged(instance, filename):
        now = datetime.datetime.now()
        path = os.path.join(now.strftime('%Y'), now.strftime('%m'),
                            now.strftime('%d'))
        hashed_filename = (hashlib.md5(filename +
                            str(now.microsecond)).hexdigest())
        __, extension = os.path.splitext(filename)
        return os.path.join(tag, path, hashed_filename + extension)
    return _upload_path_tagged


class Participant(models.Model):
    """ Participants - speakers at events. """
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, max_length=65, unique=True)
    photo = models.FileField(upload_to=_upload_path('participant-photo'),
                             blank=True)
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=50, blank=True)
    team = models.CharField(max_length=50, blank=True)
    irc = models.CharField(max_length=50, blank=True)
    topic_url = models.URLField(blank=True)
    blog_url = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    ROLE_EVENT_COORDINATOR = 'event-coordinator'
    ROLE_PRINCIPAL_PRESENTER = 'principal-presenter'
    ROLE_PRESENTER = 'presenter'
    ROLE_CHOICES = (
        (ROLE_EVENT_COORDINATOR, 'Event Coordinator'),
        (ROLE_PRINCIPAL_PRESENTER, 'Principal Presenter'),
        (ROLE_PRESENTER, 'Presenter'),
    )
    role = models.CharField(max_length=25, choices=ROLE_CHOICES)
    CLEARED_YES = 'yes'
    CLEARED_NO = 'no'
    CLEARED_FINAL_CUT = 'final-cut'
    CLEARED_CHOICES = (
        (CLEARED_YES, 'Yes'),
        (CLEARED_NO, 'No'),
        (CLEARED_FINAL_CUT, 'Final Cut'),
    )
    cleared = models.CharField(max_length=15,
                               choices=CLEARED_CHOICES, default=CLEARED_NO)

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


class Template(models.Model):
    """Provides the HTML embed codes, links, etc. for each different type of
       video or stream."""
    name = models.CharField(max_length=100)
    content = models.TextField(help_text='The HTML framework for this' +
        ' template.  Use {{ tag }} for the per-event tag.  Other Jinja2' +
        ' constructs are also allowed.  Warning! Changes affect all events' +
        ' associated with this template.')

    def __unicode__(self):
        return self.name


class EventManager(models.Manager):
    def _get_now(self):
        return datetime.datetime.utcnow().replace(tzinfo=utc)

    def _get_live_time(self):
        return (self._get_now() +
                datetime.timedelta(minutes=settings.LIVE_MARGIN))

    def initiated(self):
        return self.get_query_set().filter(status=Event.STATUS_INITIATED)

    def upcoming(self):
        return self.get_query_set().filter(status=Event.STATUS_SCHEDULED,
               archive_time=None, start_time__gt=self._get_live_time())

    def live(self):
        return self.get_query_set().filter(status=Event.STATUS_SCHEDULED,
               archive_time=None, start_time__lt=self._get_live_time())

    def archiving(self):
        return self.get_query_set().filter(status=Event.STATUS_SCHEDULED,
               archive_time__gt=self._get_now(),
               start_time__lt=self._get_now())

    def archived(self):
        return self.get_query_set().filter(status=Event.STATUS_SCHEDULED,
               archive_time__lt=self._get_now(),
               start_time__lt=self._get_now())


class Event(models.Model):
    """ Events - all the essential data and metadata for publishing. """
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, max_length=215, unique=True)
    template = models.ForeignKey(Template, blank=True, null=True)
    template_tag =  models.CharField(max_length=250, blank=True)
    STATUS_INITIATED = 'initiated'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_CHOICES = (
        (STATUS_INITIATED, 'Initiated'),
        (STATUS_SCHEDULED, 'Scheduled')
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default=STATUS_INITIATED)
    placeholder_img = models.FileField(upload_to=
                                      _upload_path('event-placeholder'))
    description = models.TextField()
    short_description = models.TextField(blank=True, help_text='Optional: ' +
                        'if not provided, this will be filled in by the ' +
                        'first words of the full description.')
    start_time = models.DateTimeField()
    archive_time = models.DateTimeField(blank=True, null=True)
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
    objects = EventManager()


class EventOldSlug(models.Model):
    """Used to permanently redirect old URLs to the new slug location."""
    event = models.ForeignKey(Event)
    slug = models.SlugField(max_length=215, unique=True)
