# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from galaxy.models import Workflow, GalaxyUser, GalaxyInstanceTracking, GalaxyFileLink, WorkflowRun, History

admin.site.register(Workflow)
admin.site.register(WorkflowRun)
admin.site.register(GalaxyUser)
admin.site.register(GalaxyInstanceTracking)
admin.site.register(GalaxyFileLink)
admin.site.register(History)

