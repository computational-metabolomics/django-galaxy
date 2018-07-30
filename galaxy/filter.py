import django_filters
from django_filters import rest_framework as filters
from galaxy.models import Workflow, History, GalaxyUser


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

class GalaxyUserFilter(django_filters.FilterSet):

    class Meta:
        model = GalaxyUser
        fields = {
            'id': ['exact'],
            'galaxyinstancetracking__name': ['contains'],
        }