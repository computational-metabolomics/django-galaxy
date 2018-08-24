# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

# general python
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.workflows import WorkflowClient
from bioblend.galaxy.client import ConnectionError

# standard django
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User

# django external apps
from dal import autocomplete

# django custom user external apps
# none

# django 'this' app
from .models import (WorkflowRun,
                     Workflow,
                     GalaxyUser,
                     GalaxyInstanceTracking,
                     FilesToGalaxyDataLibraryParam,
                     GenericFilesToGalaxyHistoryParam,
                     HistoryData)



class GalaxyInstanceTrackingForm(forms.ModelForm):
    '''
    Create a Galaxy instance to track in django. Note that the Galaxy needs to be accessible at the point of
    initialisation.

    If file transfer is required to Galaxy that is not located on the same server as the Django server then the
    associated FTP host & post details need to be added as well, see `galaxy docs`_

    Simply checks if the url is valid and can be accessed (no check performed for ftp currently)

    .. _galaxy docs: https://galaxyproject.org/ftp-upload/
    '''
    def clean_url(self):
        url = self.cleaned_data['url']

        # ctx = ssl.create_default_context()
        # ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE
        #
        # try:
        #     urllib2.urlopen(url,  context=ctx)
        # except urllib2.HTTPError, e:
        #     raise forms.ValidationError('url error:{}'.format(e.reason))
        # except urllib2.URLError, e:
        #     raise forms.ValidationError('url error:{}'.format(e.reason))

        return self.cleaned_data['url']

    class Meta:
        model = GalaxyInstanceTracking
        fields = ('url', 'name', 'ftp_host', 'ftp_port', 'galaxy_root_path', 'public')


class GalaxyUserForm(forms.ModelForm):
    '''
    Create a Galaxy User

    form checks if a duplicate entry is added and checks if the galaxy instance can be connected to with the
    user details
    '''
    def __init__(self, *args, **kwargs):
        self.internal_user = kwargs.pop('user', None)
        super(GalaxyUserForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        print(self.internal_user)

        # check to make sure a duplicate entry is not being submitted
        git = cleaned_data['galaxyinstancetracking']
        try:
            GalaxyUser.objects.get(galaxyinstancetracking=git,
                                   internal_user=self.internal_user)
        except GalaxyUser.DoesNotExist:
            pass
        else:
            raise ValidationError('The current user ({}) is already assigned to the chosen Galaxy'
                                  ' instance ({}) '.format(self.internal_user, git.name))

        # check galaxy instance can be accessed and is useable
        api_key = cleaned_data['api_key']
        galaxy_url = git.url
        check_galaxy(api_key, galaxy_url)

        return cleaned_data

    class Meta:
        model = GalaxyUser
        fields = ('api_key', 'galaxyinstancetracking', 'email', 'public')
        widgets = {
            'galaxyinstancetracking': autocomplete.ModelSelect2(url='galaxyinstancetracking-autocomplete'),
        }




class HistoryDataForm(forms.ModelForm):
    # choose what measurement to select along with the LC to perform on each
    # SPE column.

    def __init__(self, *args, **kwargs):
        super(HistoryDataForm, self).__init__(*args, **kwargs)
        self.fields['history'].disabled = True
        self.fields['name'].disabled = True

    class Meta:
        model = HistoryData
        fields = ('history', 'name')




class WorkflowRunForm(forms.ModelForm):

    class Meta:
        model = WorkflowRun
        fields = ('history_name', 'library')

class WorkflowForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(WorkflowForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Workflow
        fields = ( 'workflowjson', 'name', 'description', 'galaxyinstancetracking')
        widgets = {
            'galaxyinstancetracking': autocomplete.ModelSelect2(url='galaxyinstancetracking-autocomplete'),
        }

    def clean(self):
        cleaned_data = super(WorkflowForm, self).clean()

        if any(self.errors):
            return self.errors

        # Check galaxy is accessible and works
        user = User.objects.get(username=self.user)
        git = cleaned_data['galaxyinstancetracking']
        api_key = GalaxyUser.objects.get(internal_user=user, galaxyinstancetracking=git).api_key
        galaxy_url = git.url
        check_galaxy(api_key, galaxy_url)

        # basic check to see if the json has some of the standard workflow parameters (only checking name at the
        # moment)
        wf = cleaned_data['workflowjson']
        try:
            wf['name']
        except KeyError as e:
            raise forms.ValidationError('Galaxy workflow file in incorrect format (missing name)')

        return cleaned_data

def check_galaxy(api_key, galaxy_url):
    gi = GalaxyInstance(galaxy_url, key=api_key)
    gi.verify = False
    wc = WorkflowClient(gi)
    try:
        wc.get_workflows()
    except ConnectionError as e:
        raise forms.ValidationError('Something is wrong with Galaxy connection, please check')


class FilesToGalaxyDataLibraryParamForm(forms.ModelForm):

    galaxy_password = forms.CharField(label='Galaxy password',
                                      widget=forms.PasswordInput(),
                                      required=False,help_text='Only required if using ftp')

    def __init__(self, *args, **kwargs):
        # type: (object, object) -> object
        self.user = kwargs.pop('user', None)
        super(FilesToGalaxyDataLibraryParamForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FilesToGalaxyDataLibraryParam
        fields = ('folder_name', 'galaxyinstancetracking', 'link2files', 'local_path', 'ftp')
        widgets = {
            'galaxyinstancetracking': autocomplete.ModelSelect2(url='galaxyinstancetracking-autocomplete'),
        }

    def clean(self):
        cleaned_data = super(FilesToGalaxyDataLibraryParamForm, self).clean()

        ftp = cleaned_data['ftp']
        galaxy_p = cleaned_data['galaxy_password']

        l2f = cleaned_data['link2files']

        if any(self.errors):
            return self.errors

        if ftp and not galaxy_p:
            raise forms.ValidationError('If using ftp the Galaxy password for the current user is required')

        if l2f and ftp:
            raise forms.ValidationError('Link2files is not possible when using FTP')


        return cleaned_data


class GenericFilesToGalaxyHistoryParamForm(forms.ModelForm):

    galaxy_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        # type: (object, object) -> object
        self.user = kwargs.pop('user', None)
        super(GenericFilesToGalaxyHistoryParamForm, self).__init__(*args, **kwargs)

    class Meta:
        model =  GenericFilesToGalaxyHistoryParam
        fields = ('history_name', 'galaxyinstancetracking')
        widgets = {
            'galaxyinstancetracking': autocomplete.ModelSelect2(url='galaxyinstancetracking-autocomplete'),
        }


class DeleteGalaxyHistoryForm(forms.Form):
    purge = forms.BooleanField(label='Purge', required=False)




