from django.conf.urls import url
import views

urlpatterns = [

    url(r'galaxy_summary/$', views.GalaxySummaryView.as_view(), name='galaxy_summary'),
    url(r'addgi/$', views.GalaxyInstanceCreateView.as_view(), name='addgi'),
    url(r'addguser/$', views.GalaxyUserCreateView.as_view(), name='addguser'),
    url(r'addworkflow/$', views.WorkflowCreateView.as_view(), name='addworkflow'),
    url(r'galaxy_sync/$', views.GalaxySync.as_view(), name='galaxy_sync'),
    url(r'workflow_summary/$', views.WorkflowListView.as_view(), name='workflow_summary'),
    url(r'files_to_galaxy_datalib/$', views.FilesToGalaxyDataLib.as_view(), name='files_to_galaxy_datalib'),
    url(r'files_to_galaxy_history/$', views.GenericFilesToGalaxyHistory.as_view(), name='files_to_galaxy_history'),
    url(r'runworkflow/(?P<wid>\d+)$', views.WorkflowRunView.as_view(), name='runworkflow'),
    url(r'^success/$', views.success, name='success'),
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