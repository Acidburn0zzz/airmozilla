import pytz

from django import forms
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.utils.timezone import get_current_timezone_name

from funfactory.urlresolvers import reverse

from airmozilla.base.forms import BaseModelForm
from airmozilla.main.models import (Category, Event, EventOldSlug, Location,
                                    Participant, Tag, Template)


TIMEZONE_CHOICES = [(tz, tz.replace('_', ' ')) for tz in pytz.common_timezones]


class UserEditForm(BaseModelForm):
    class Meta:
        model = User
        fields = ('is_active', 'is_staff', 'is_superuser',
                  'groups', 'user_permissions')


class GroupEditForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupEditForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        choices = self.fields['permissions'].choices
        self.fields['permissions'] = forms.MultipleChoiceField(choices=choices,
                                           widget=forms.CheckboxSelectMultiple,
                                           required=False)

    class Meta:
        model = Group


class UserFindForm(BaseModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError('User with this email not found.')
        return user.email


class EventRequestForm(BaseModelForm):
    tags = forms.CharField()
    participants = forms.CharField()
    timezone = forms.ChoiceField(choices=TIMEZONE_CHOICES,
                     initial=settings.TIME_ZONE)
    def __init__(self, *args, **kwargs):
        super(EventRequestForm, self).__init__(*args, **kwargs)
        self.fields['participants'].help_text = (
             '<a href="%s" class="btn" target="_blank">'
             '<i class="icon-plus-sign"></i>'
             'New Participant'
             '</a>' % reverse('manage:participant_new'))
        self.fields['location'].help_text = (
            '<a href="%s" class="btn" target="_blank">'
            '<i class="icon-plus-sign"></i>'
            'New location'
            '</a>' % reverse('manage:location_new'))

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        split_tags = [t.strip() for t in tags.split(',') if t.strip()]
        final_tags = []
        for tag_name in split_tags:
            t, __ = Tag.objects.get_or_create(name=tag_name)
            final_tags.append(t)
        return final_tags

    def clean_participants(self):
        participants = self.cleaned_data['participants']
        split_participants = [p.strip() for p in participants.split(',')
                              if p.strip()]
        final_participants = []
        for participant_name in split_participants:
            p = Participant.objects.get(name=participant_name)
            final_participants.append(p)
        return final_participants

    def clean_slug(self):
        """Enforce unique slug across current slugs and old slugs."""
        slug = self.cleaned_data['slug']
        if (Event.objects.filter(slug=slug).exclude(pk=self.instance.id)
                  or EventOldSlug.objects.filter(slug=slug)):
            raise forms.ValidationError('This slug is already in use.')
        return slug

    class Meta:
        model = Event
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'call_info': forms.Textarea(attrs={'rows': 3}),
            'additional_links': forms.Textarea(attrs={'rows': 3}),
            'template_environment': forms.Textarea(attrs={'rows': 3}),
            'additional_links': forms.Textarea(attrs={'rows': 3}),
            'start_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M'),
            'archive_time': forms.DateTimeInput(format='%Y-%m-%d %H:%M'),
        }
        exclude = ('featured', 'status', 'archive_time')
        # Fields specified to enforce order
        fields = ('title', 'slug', 'placeholder_img', 'description',
        'short_description', 'location', 'start_time', 'timezone',
        'participants', 'category', 'tags', 'call_info', 'additional_links',
        'public')


class EventEditForm(EventRequestForm):
    class Meta(EventRequestForm.Meta):
        exclude = ()
        # Fields specified to enforce order
        fields = ('title', 'slug', 'status', 'public', 'featured', 'template',
        'template_environment', 'placeholder_img', 'location', 'description',
        'short_description', 'start_time', 'archive_time', 'timezone',
        'participants', 'category', 'tags', 'call_info', 'additional_links')


class EventFindForm(BaseModelForm):
    class Meta:
        model = Event
        fields = ('title',)

    def clean_title(self):
        title = self.cleaned_data['title']
        if not Event.objects.filter(title__icontains=title):
            raise forms.ValidationError('No event with this title found.')
        return title


class ParticipantEditForm(BaseModelForm):
    class Meta:
        model = Participant


class ParticipantFindForm(BaseModelForm):
    class Meta:
        model = Participant
        fields = ('name',)

    def clean_name(self):
        name = self.cleaned_data['name']
        if not Participant.objects.filter(name__icontains=name):
            raise forms.ValidationError('No participant with this name found.')
        return name


class CategoryForm(BaseModelForm):
    class Meta:
        model = Category


class TemplateEditForm(BaseModelForm):
    class Meta:
        model = Template
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20})
        }


class LocationEditForm(BaseModelForm):
    timezone = forms.ChoiceField(choices=TIMEZONE_CHOICES)
    def __init__(self, *args, **kwargs):
        super(LocationEditForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            initial = kwargs['instance'].timezone
        else:
            initial = settings.TIME_ZONE
        self.fields['timezone'].initial = initial
    class Meta:
        model = Location
