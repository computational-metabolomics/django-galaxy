# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime
import os
#from django_mysql.models import JSONField
from gfiles.models import GenericFile
from django.utils.text import slugify
import json

def workflow_file_store(instance, filename):
    now = datetime.now()
    return os.path.join('galaxy', 'workflows',now.strftime("%Y_%m_%d"), filename)

def history_file_store(instance, filename):
    now = datetime.now()
    return os.path.join('galaxy', 'history', now.strftime("%Y_%m_%d"), filename)


class GalaxyInstanceTracking(models.Model):
    '''
    Model for tracking Galaxy instances and associated ftp sites
    '''

    url = models.URLField()  # dodgy urls are checked at the form level
    name = models.CharField(max_length=200, unique=True)
    ftp_host = models.CharField(max_length=200, blank=True, null=True,
                                help_text='The ftp host and port are required if the file server '
                                                        'and galaxy server cannot be connected either direcly or via symlink)')
    ftp_port = models.IntegerField(blank=True, null=True, default=21)
    galaxy_root_path = models.CharField(max_length=500, blank=True, null=True, help_text='If the Galaxy instance is accessible '
                                                                                         'either via a symlink or directly, the '
                                                                                         'path should be included here')

    public = models.BooleanField(default=True, help_text='When set to true, other users will able to see and use '
                                                         'this Galaxy instance')

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, help_text='The user who created the link with this'
                                                                        ' Galaxy instance',
                             null=True, blank=True)

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)

        return super(GalaxyInstanceTracking, self).save(*args, **kwargs)

    def user_count(self):
        return len(GalaxyUser.objects.filter(galaxyinstancetracking_id=self.id))


class GalaxyUser(models.Model):
    '''
    Model for linking a Galaxy user to a Django user

    A django user can be linked to many Galaxy instances and each Galaxy User
    HAS to be linked to Galaxy instance

    django-user [1 --- *] galaxy-users

    galaxy-user [* --- 1] galaxy-instances

    However, a django user can't be linked to multiple of the same
    galaxy instances

    '''

    internal_user = models.ForeignKey(User, on_delete=models.CASCADE, help_text='The internal user for '
                                                                                'the Django (MOGI) web application. '
                                                                                'i.e. the User from this web application'
                                                                                ' that is linking to the Galaxy user')
    email = models.EmailField(null=False, help_text='the email used for the Galaxy account')

    # API currently not hashed, tried to follow the salting procedure (https://djangosnippets.org/snippets/1330/)
    # but think it does not work on Python2. Something to look into later but not essential for the work
    # we are doing. Also.... if you are worried about security you probably not going to use Galaxy anyway......
    api_key = models.CharField(max_length=200, null=False)
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE)
    public = models.BooleanField(default=False, help_text='By default no other users can your Galaxy user connections')

    def __str__(self):  # __unicode__ on Python 2
        return 'g-user for dj-user {}'.format(self.user)

    class Meta:
        unique_together = (("internal_user", "galaxyinstancetracking"),)


class Workflow(models.Model):
    '''
    Model for Galaxy workflows. The workflow needs to be associated with a Valid Galaxy instance
    '''
    workflowjson = models.TextField(max_length=5000, blank=False, null=False)
    name = models.CharField(max_length=200, null=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    galaxy_id = models.CharField(max_length=200)
    latest_workflow_uuid = models.CharField(max_length=200)
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE, null=True,
                                       help_text='The galaxy instance the Workflow should currently be performed on')
    accessible = models.BooleanField(null=False, default=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    def save(self, *args, **kwargs):
        super(Workflow, self).save(*args, **kwargs)

        data_inputs = []
        steps = self.workflowjson['steps']

        WorkflowInput.objects.filter(workflow_id=self.id).delete()

        data_inputs = []
        for step, details, in steps.items():
            dtype = details['type']
            name = details['label']
            if dtype == 'data_input' or dtype == 'data_collection_input':
                data_inputs.append({'step': step, 'dtype': dtype, 'name': name})

        WorkflowInput.objects.bulk_create(
             [WorkflowInput(step=d['step'], datatype=d['dtype'], name=d['name'], workflow_id=self.id) for d in data_inputs]
        )


class History(models.Model):
    update_time = models.CharField(max_length=200)
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    empty = models.IntegerField()
    error = models.IntegerField()
    failed_metadata = models.IntegerField()
    new = models.IntegerField()
    ok = models.IntegerField()
    paused = models.IntegerField()
    running = models.IntegerField()
    queued = models.IntegerField()
    setting_metadata = models.IntegerField()
    upload = models.IntegerField()
    galaxy_id = models.CharField(max_length=200, null=False, blank=False)
    estimated_progress = models.FloatField()
    # running_tasks_details = tables.Column()

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    class Meta:
        unique_together = (("galaxyinstancetracking", "galaxy_id"),)







class WorkflowInput(models.Model):
    name = models.CharField(max_length=200, null=True)
    step = models.CharField(max_length=200, null=False)
    datatype = models.CharField(max_length=200, null=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)

    def __str__(self):              # __unicode__ on Python 2
        return '{}_{}'.format(self.step, self.datatype)

class WorkflowRun(models.Model):
    rundate = models.DateTimeField(auto_now_add=True)
    ran_by = models.ForeignKey(User, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    library = models.BooleanField(help_text='Use files from data library')
    history_name = models.CharField(max_length=200, null=False)

    def __str__(self):              # __unicode__ on Python 2
        return self.rundate


class GalaxyFileLink(models.Model):
    galaxy_id = models.CharField(max_length=250)
    galaxy_library = models.BooleanField(null=False, default=True)
    genericfile = models.ForeignKey(GenericFile, on_delete=models.CASCADE)
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE)
    removed = models.BooleanField(default=False, help_text='if the Galaxy file has either been purged or deleted. However'
                                                   ' the "deleted" options does not seem to be recorded correctly'
                                                   ' for ldda (library dasasets) by Galaxy so can be a bit '
                                                   ' misleading. However if we can no longer access the '
                                                   ' file in Bioblend then this should be set to True.')
    def __str__(self):              # __unicode__ on Python 2
        return '{}_removed-{}'.format(self.galaxy_id, self.removed)

    class Meta:
        unique_together = (("galaxyinstancetracking", "galaxy_id"),)


class FilesToGalaxyDataLibraryParam(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=200, null=True, blank=True)
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE)
    link2files = models.BooleanField(default=False)
    local_path = models.BooleanField(default=False)
    ftp = models.BooleanField(default=True, help_text='Use FTP file transfer to copy the files over to the '
                                                      'Galaxy instance')
    remove = models.BooleanField(default=False,
                                 help_text='Remove any existing data for the selected ISA projects in the '
                                           ' Galaxy data libraries')

    def __str__(self):  # __unicode__ on Python 2
        return 'Files uploaded to dj-user {}'.format(self.folder_name, self.added_by)


class GenericFilesToGalaxyHistoryParam(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    history_name = models.CharField(max_length=200, null=False)
    galaxyinstancetracking = models.ForeignKey(GalaxyInstanceTracking, on_delete=models.CASCADE)

    def __str__(self):  # __unicode__ on Python 2
        return 'Files uploaded to dj-user {}'.format(self.history_name, self.added_by)


def history_data_file_store(instance, filename):
    now = datetime.now()
    return os.path.join('data', 'files', 'ghistory', 'data', now.strftime("%Y_%m_%d"), filename)


class HistoryData(GenericFile):
    history = models.ForeignKey(History, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    # added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # create_time = models.CharField(max_length=200)
    # creating_job = models.CharField(max_length=200)
    # data_type = models.CharField(max_length=200)
    # dataset_id = models.CharField(max_length=200)
    # deleted = models.CharField(max_length=200)
    # download_url = models.CharField(max_length=200)
    # file_name = models.CharField(max_length=200)
    # hda_ldda = models.CharField(max_length=200)
    # history_content_type = models.CharField(max_length=200)
    # history_id = models.CharField(max_length=200)
    # id = models.CharField(max_length=200)
    # model_class = models.CharField(max_length=200)
    # name = models.CharField(max_length=200)
    # purged = models.CharField(max_length=200)
    # state = models.CharField(max_length=200)
    # type = models.CharField(max_length=200)
    # update_time = models.CharField(max_length=200)
    # history_data_file = models.FileField(upload_to=history_data_file_store, blank=False, null=False)

    def __str__(self):  # __unicode__ on Python 2
        return self.name





