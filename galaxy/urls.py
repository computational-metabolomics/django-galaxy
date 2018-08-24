from django.conf.urls import url
from galaxy import views

urlpatterns = [

    url(r'^$', views.GalaxySummaryView.as_view(), name='galaxy_summary'),
    # galaxy instances
    url(r'add_galaxy_instance/$', views.GalaxyInstanceCreateView.as_view(), name='add_galaxy_instance'),
    url(r'update_galaxy_instance/(?P<pk>\d+)/$', views.GalaxyInstanceTrackingUpdateView.as_view(), name='update_galaxy_instance'),
    url(r'delete_galaxy_instance/(?P<pk>\d+)/$', views.GalaxyInstanceTrackingDeleteView.as_view(), name='delete_galaxy_instance'),
    url(r'^galaxyinstancetracking-autocomplete/$',
        views.GalaxyInstanceTrackingAutocomplete.as_view(),
        name='galaxyinstancetracking-autocomplete'),

    # galaxy users
    url(r'add_galaxy_user/$', views.GalaxyUserCreateView.as_view(), name='add_galaxy_user'),
    url(r'update_galaxy_user/(?P<pk>\d+)/$', views.GalaxyUserUpdateView.as_view(), name='update_galaxy_user'),
    url(r'delete_galaxy_user/(?P<pk>\d+)/$', views.GalaxyUserDeleteView.as_view(), name='delete_galaxy_user'),
    url(r'list_galaxy_user/$', views.GalaxyUserListView.as_view(), name='list_galaxy_user'),

    url(r'addworkflow/$', views.WorkflowCreateView.as_view(), name='addworkflow'),
    url(r'galaxy_sync/$', views.GalaxySync.as_view(), name='galaxy_sync'),
    url(r'workflow_summary/$', views.WorkflowListView.as_view(), name='workflow_summary'),
    url(r'files_to_galaxy_datalib/$', views.FilesToGalaxyDataLib.as_view(), name='files_to_galaxy_datalib'),
    url(r'files_to_galaxy_history/$', views.GenericFilesToGalaxyHistory.as_view(), name='files_to_galaxy_history'),
    url(r'runworkflow/(?P<wid>\d+)$', views.WorkflowRunView.as_view(), name='runworkflow'),
    url(r'^galaxy_success/$', views.success, name='galaxy_success'),
    url(r'^checkbox_selected/$', views.checkbox_selected, name='checkbox_selected'),
    url(r'^workflow_status/$', views.WorkflowStatus.as_view(), name='workflow_status'),
    url(r'^workflow_status/_export=csv$', views.WorkflowStatus.as_view(), name='workflow_status_csv'),
    url(r'^workflow_status_update/$', views.workflow_status_update, name='workflow_status_update'),
    url(r'^history_status_update/$', views.history_status_update, name='history_status_update'),

    url(r'^history_status/$', views.HistoryListView.as_view(), name='history_status'),
    url(r'^history_data_bioblend_list/(?P<pk>\d+)$', views.HistoryDataBioBlendListView.as_view(), name='history_data_bioblend_list'),



    url(r'^history_data_create/(?P<history_internal_id>\d+)/(?P<galaxy_id>\w+)$', views.HistoryDataCreateView.as_view(), name='history_data_create'),
    # url(r'^contact/$', views.ContactWizard.as_view([ContactForm1, ContactForm2])),
]