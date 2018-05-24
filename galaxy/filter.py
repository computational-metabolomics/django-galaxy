import django_filters
from django_filters import rest_framework as filters
from .models import Workflow, History


class WorkflowFilter(filters.FilterSet):

    class Meta:
        model = Workflow
        fields = {
            'name': ['contains'],
            'galaxy_id': ['contains'],
            # 'accessible': ['isnull']
        }




class HistoryFilter(django_filters.FilterSet):

    class Meta:
        model = History
        fields = {
            'id': ['exact'],
            'galaxy_id': ['exact'],
            'galaxyinstancetracking__name': ['contains'],
            'name': ['contains'],
            'update_time': ['contains'],
            'new': ['range'],
            'error': ['range'],
            'queued': ['range'],
            'ok': ['range'],
            'running': ['range']

        }