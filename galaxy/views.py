# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
# general python
import json
from datetime import datetime
import operator
import re
import six
import sys

if sys.version_info > (3, 0):
    from functools import reduce

# standard django
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, DeleteView, UpdateView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

# django external apps
from django_tables2 import RequestConfig
import django_tables2 as tables
from django_tables2.views import SingleTableMixin, MultiTableMixin
from django_filters.views import FilterView
from django_tables2.export.views import ExportMixin
from dal import autocomplete

# django custom user external apps
from gfiles.models import GenericFile
from gfiles.views import GFileListView
from gfiles.filter import GFileFilter
from gfiles.tables import GFileTable

# django 'this' app
from galaxy.forms import (
    WorkflowForm,
    FilesToGalaxyDataLibraryParamForm,
    GenericFilesToGalaxyHistoryParamForm,
    GalaxyUserForm,
    WorkflowRunForm,
    GalaxyInstanceTrackingForm,
    DeleteGalaxyHistoryForm,
    HistoryDataForm
)
from galaxy.models import (
    GalaxyInstanceTracking,
    GalaxyUser,
    Workflow,
    History,
    HistoryData
)
from galaxy.tables import (
    WorkflowStatusTable,
    WorkflowTable,
    HistoryTable,
    HistoryDataTable,
    GalaxyInstanceTrackingTable,
    GalaxyUserTable
)
from galaxy.filter import (
    WorkflowFilter,
    HistoryFilter,
    GalaxyUserFilter
)

from galaxy.utils.upload_to_galaxy import f2dl_action, f2h_action
from galaxy.utils.sync_files import sync_galaxy_files
from galaxy.utils.workflow_actions import (
    run_galaxy_workflow,
    get_workflow_status,
    workflow_sync
)
from galaxy.utils.history_actions import (
    get_history_status,
    delete_galaxy_histories,
    get_history_data,
    init_history_data_save_form,
    history_data_save_form
)

TABLE_CLASS = "mogi table-bordered table-striped table-condensed table-hover"



class GalaxyInstanceCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    '''
    Create a Galaxy instance to track in django. Note that the Galaxy needs to be accessible at the point of
    initialisation.

    If file transfer is required to Galaxy that is not located on the same server as the Django server then the
    associated FTP host & post details need to be added as well, see `galaxy docs`_

    User login required

    .. _galaxy docs: https://galaxyproject.org/ftp-upload/
    '''
    model = GalaxyInstanceTracking
    success_url = reverse_lazy('galaxy_summary')
    form_class = GalaxyInstanceTrackingForm
    success_message = 'Galaxy instance tracked'

    def form_valid(self, form):
        # The user is automatically added to the model based on whoever is logged in at the time
        gi = form.save(commit=False)
        gi.owner = self.request.user
        gi.save()
        return super(GalaxyInstanceCreateView, self).form_valid(form)


class GalaxyInstanceTrackingUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = GalaxyInstanceTracking
    success_url = reverse_lazy('galaxy_summary')
    form_class = GalaxyInstanceTrackingForm
    success_message = 'Galaxy instance tracking updated'

    def user_passes_test(self, request):
        if request.user.is_superuser:
            return True
        elif request.user.is_authenticated():
            return self.get_object().owner == request.user
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            messages.error(request, 'User has insufficient privileges to update Galaxy instance tracking')
            return redirect('galaxy_summary')
        return super(GalaxyInstanceTrackingUpdateView, self).dispatch(request, *args, **kwargs)



class GalaxyInstanceTrackingDeleteView(LoginRequiredMixin, DeleteView):
    model = GalaxyInstanceTracking
    success_url = reverse_lazy('galaxy_summary')
    template_name = 'galaxy/confirm_delete.html'

    def user_passes_test(self, request):
        if request.user.is_superuser:
            return True
        elif request.user.is_authenticated():
            return self.get_object().owner == request.user
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            messages.error(request, 'User has insufficient privileges to delete Galaxy instance tracking')
            return redirect('galaxy_summary')
        messages.error(request, 'Galaxy instance tracking deleted')
        return super(GalaxyInstanceTrackingDeleteView, self).dispatch(request, *args, **kwargs)


class GalaxyInstanceTrackingAutocomplete(autocomplete.Select2QuerySetView):
    model_class = GalaxyInstanceTracking

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return self.model_class.objects.none()
        if self.request.user.is_superuser:
            qs = self.model_class.objects.all()
        else:
            qs = self.model_class.objects.filter(Q(public=True) | Q(owner=self.request.user))

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class GalaxySummaryView(LoginRequiredMixin, SingleTableMixin, ListView):
    # initial = {'key': 'value'}
    template_name = 'galaxy/galaxy_summary.html'
    table_class = GalaxyInstanceTrackingTable
    model = GalaxyInstanceTracking

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return self.model.objects.none()
        if self.request.user.is_superuser:
            return self.model.objects.all()
        else:
            return self.model.objects.filter(Q(public=True) | Q(owner=self.request.user))



class GalaxyUserCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    '''
    Register a Galaxy user to a Galaxy instance that we have tracked.

    A django user can be linked to many Galaxy instances and each Galaxy User HAS to be linked to Galaxy instance

    django-user [1 --- *] galaxy-users

    galaxy-user [* --- 1] galaxy-instances

    However, a django user can't be linked to multiple of the same galaxy instances

    '''
    model = GalaxyUser
    success_url = reverse_lazy('list_galaxy_user')
    form_class = GalaxyUserForm
    success_message = 'Galaxy User added'

    def get_form_kwargs(self):
        # Get the user form as a kwarg argument
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # The user is automatically added to the model based on whoever is logged in at the time
        gu = form.save(commit=False)
        gu.internal_user = self.request.user
        gu.save()
        return super(GalaxyUserCreateView, self).form_valid(form)

    # def get_initial(self):
    #     # show the most recent galaxy instance as default value
    #     return {'galaxyinstancetracking':GalaxyInstanceTracking.objects.last()}





class GalaxyUserUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = GalaxyUser
    success_url = reverse_lazy('list_galaxy_user')
    form_class = GalaxyUserForm
    success_message = 'Galaxy user has been updated'

    def user_passes_test(self, request):
        if request.user.is_superuser:
            return True
        elif request.user.is_authenticated():
            return self.get_object().internal_user == request.user
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            messages.error(request, 'User has insufficient privileges to update Galaxy user')
            return redirect('galaxy_summary')

        return super(GalaxyUserUpdateView, self).dispatch(request, *args, **kwargs)


class GalaxyUserDeleteView(DeleteView):
    model = GalaxyUser
    success_url = reverse_lazy('list_galaxy_user')
    template_name = 'galaxy/confirm_delete.html'

    def user_passes_test(self, request):
        if request.user.is_superuser:
            return True
        elif request.user.is_authenticated():
            return self.get_object().internal_user == request.user
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.user_passes_test(request):
            messages.error(request, 'User has insufficient privileges to delete Galaxy user')
            return redirect('galaxy_summary')

        messages.error(request, 'User has insufficient privileges to delete')
        return super(GalaxyUserDeleteView, self).dispatch(request, *args, **kwargs)



class GalaxyUserListView(LoginRequiredMixin, SingleTableMixin, ListView):
    # initial = {'key': 'value'}
    template_name = 'galaxy/galaxy_user_list.html'
    table_class = GalaxyUserTable
    model = GalaxyUser

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return self.model.objects.none()
        if self.request.user.is_superuser:
            return self.model.objects.all()
        else:
            return self.model.objects.filter(Q(public=True) | Q(internal_user=self.request.user))


class GalaxySync(LoginRequiredMixin, View):
    '''
    Sync workflows from available galaxy instances for the current user.

    This will add any workflows to the django database that have not already been added. And will update
    any that have been updated on the galaxy instance.

    todo: It might be worth changing this view to a more general GalaxySync option. That syncs workflows & files
    '''
    def get(self, request, *args, **kwargs):
        return render(request, 'galaxy/galaxy_sync.html')

    def post(self, request, *args, **kwargs):
        workflow_sync(request.user)
        sync_galaxy_files(request.user)
        get_history_status(request.user)
        # redirects to show the current available workflows
        return redirect('workflow_summary')


class WorkflowListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    '''
    View and initiate a run for all registered workflows.

    Workflows can also be synced here as well
    '''
    table_class = WorkflowTable
    redirect_to = 'workflow_summary'
    model = Workflow
    template_name = 'galaxy/workflow_summary.html'
    filterset_class = WorkflowFilter

    def post(self, request, *args, **kwargs):
        workflow_sync(request.user)
        # redirects to show the current available workflows
        return redirect(self.redirect_to)


class TableFileSelectMixin:
    '''
    General class for file selection with ajax multipage
    '''
    success_msg = ""
    success_url = '/galaxy/success'
    table_pagination = {"per_page": 15}
    # form_class =  GenericFilesToGalaxyDataLibraryParamForm   # should add generic form for this, perhaps based on a related model
    # template_name = 'galaxy/files_to_galaxy.html'   # should add generic template for this, perhaps based on a related model
    initial_context = {}  # pass any default parameters required for any context that is used

    def get(self, request, *args, **kwargs):
        # we have to overide the standard get to add some extra information to the context

        form = self.form_class()
        context = self.form2context(form)

        return render(request, self.template_name, context=context)

    def form2context(self, form):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        self.object_list = self.filterset.qs
        context = self.get_context_data(filter=self.filterset, object_list=self.object_list,  form=form)
        context.update(self.initial_context)



        return context

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            form = self.form_class()
            context = self.form2context(form)
            # keep track of the checkboxes that have been added by the user
            request = ajax_post_selected(request)

            return render(request, self.template_name, context=context)
        else:
            form = self.form_class(request.POST, request.FILES)
            context = self.form2context(form)

            if form.is_valid():
                return self.form_valid(request, form)
            else:
                return render(request, self.template_name, context=context)

    def form_valid(self, request, form):
        # first save the form and the user who posted
        return render(request, 'gfiles/submitted.html')


class FilesToGalaxyDataLib(LoginRequiredMixin, TableFileSelectMixin, GFileListView):
    '''
    Select Files to be added to Galaxy data Library

    Inherit the GFileListView that view that shows current files and allows some basic filtering
    '''
    template_name = 'galaxy/files_to_galaxy.html'
    form_class = FilesToGalaxyDataLibraryParamForm
    initial_context = {'library': True, 'django_url': '/galaxy/files_to_galaxy_datalib/'}

    def save_form_param(self, request, form):
        user = request.user
        f2dl = form.save(commit=False)
        f2dl.added_by = user
        if not f2dl.folder_name:
            now = datetime.now()
            f2dl.folder_name = '{}_{}'.format(user.username, now.strftime("%Y_%m_%d"))
        f2dl.save()
        return f2dl

    def form_valid(self, request, form):
        # first save the form and the user who posted
        f2dl = self.save_form_param(request, form)

        # then get the ids of the files that were used, and add the files to the galaxy library
        pks = request.POST.getlist("check")

        f2dl_action(pks, f2dl, galaxy_pass=form.cleaned_data['galaxy_password'])
        # reset the form checkboxes
        request.session['selected_items'] = ''
        return render(request, 'gfiles/submitted.html')


class GenericFilesToGalaxyHistory(LoginRequiredMixin, TableFileSelectMixin, GFileListView):

    template_name = 'galaxy/files_to_galaxy.html'

    form_class = GenericFilesToGalaxyHistoryParamForm
    initial_context = {'library': False, 'django_url': '/galaxy/files_to_galaxy_datalib/'}

    def form_valid(self, request, form):
        user = self.request.user
        f2h = form.save(commit=False)
        f2h.added_by = user
        f2h.save()

        pks = request.POST.getlist("check")

        f2h_action(pks, f2h, galaxy_pass=form.cleaned_data['galaxy_password'])
        return render(request, 'gfiles/submitted.html')



class WorkflowRunView(LoginRequiredMixin, View):
    '''
    Run a registered workflow
    '''
    success_msg = "Run started"
    success_url = '/galaxy/success'
    template_name = 'galaxy/workflow_run.html'
    table_class = GFileTable
    filter_class = GFileFilter
    form_class = WorkflowRunForm
    redirect_to = 'history_status'


    def update_workflow_inputs(self, l):
        # update the worklow inputs before submission (to be used with classes that inherit this class
        return l


    def get_queryset(self):
        return Workflow.objects.get(pk=self.kwargs['wid'])

    def get_datainputs(self):
        w = self.get_queryset()
        return w.workflowinput_set.all()

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        l = self.page_setup(request)
        return render(request, self.template_name, {'form': form, 'list': l, 'wid':self.kwargs['wid']})

    def page_setup(self, request):
        # Dynamic number of tables are added to the template based on what the workflow-inputs are (e.g. if
        # there are multiple data-inputs or data-input-collections). The choice of files to choose is based
        # on what the user has uploaded previously to either the gfiles or mfiles applications

        data_inputs = self.get_datainputs()
        tables_l = []
        filters = []
        data_input_names = []
        data_input_steps = []
        data_input_types = []

        # Need to setup a config for the tables (only 1 required per template page)
        rc = RequestConfig(request, paginate={'per_page': 10})

        # Get all the generic files (this will include all the mfiles as well, as the MFiles inherits the genericfile
        # class.
        # At the moment it is hard coded to include galaxy_library. But I wan't to put some javascript in so
        # the user can choose between files that have been registered with the galaxy library or with galaxy history
        # (needs to be distinct because we allow files to be added to galaxy multiple times)
        gfqs = GenericFile.objects.filter(galaxyfilelink__galaxy_library=True, galaxyfilelink__removed=False).distinct()

        # loop through all the data_inputs from the associated workflow
        for i in range(0, len(data_inputs)):

            # create a few lists of Input Datasetvarious useful information for the template
            di = data_inputs[i]
            data_input_names.append(di.name)
            data_input_steps.append(di.step)
            data_input_types.append(di.datatype)
            print('name', di.name)
            if not di.name:
                gfqs_f = gfqs
            else:
                mtch = re.match('.*\((.*)\).*', di.name)

                if mtch:
                    filetypes = mtch.group(1)
                    filetype_l = filetypes.split(',')
                    print('FILETYPE LIST', filetype_l)

                    filetype_l = [f.strip() for f in filetype_l]
                    # https://stackoverflow.com/questions/4824759/django-query-using-contains-each-value-in-a-list
                    query = reduce(operator.or_, (Q(original_filename__icontains=item) for item in filetype_l))
                    # will output something like this
                    # <Q: (OR: ('original_filename__icontains', '.txt'), ('original_filename__icontains', '.tsv'),
                    # ('original_filename__icontains', '.tabular'))>
                    print(query)
                    gfqs_f = gfqs.filter(query)
                    print(gfqs_f)
                else:
                    gfqs_f = gfqs

            # Create an invidivual filter for each table
            f = self.filter_class(request.GET, queryset=gfqs_f, prefix=i)

            # Create a checkbox column for each table, so that the javascript can see which checkbox has been
            # selected
            check = tables.CheckBoxColumn(accessor="pk",
                                          attrs={
                                              "th__input": {"onclick": "toggle(this)"},
                                              "td__input": {"onclick": "addfile(this)"}},
                                          orderable=False)

            # create a new table with the custom column
            table = self.table_class(f.qs, prefix=i, extra_columns=(('check{}'.format(i), check),),
                               attrs={'name':i, 'id':i, 'class': TABLE_CLASS})

            # load the table into the requestconfig
            rc.configure(table)

            # add the tables and filters to the list used in the template
            tables_l.append(table)
            filters.append(f)

        # create a list of all the information. Using a simple list format as it is just easy to use in the template
        l = zip(tables_l, filters, data_input_names, data_input_steps, data_input_types)
        return l

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        l = self.page_setup(request)

        if request.is_ajax():
            # the ajax is used to get to record the chosen files
            request = ajax_post_selected(request)
            return render(request, self.template_name, {'form': form, 'list': l, 'wid':self.kwargs['wid']})

        if form.is_valid():
            # if valid then we can save the run form for tracking who has performed what
            wr = form.save(commit=False)
            wr.ran_by = request.user
            wr.workflow = self.get_queryset()
            wr.save()

            # Now get the files we want to use for the workflow
            # Table prefix is the the id for the PKD
            pkd = selected_items_2_pks(json.loads(request.session['selected_items']))

            # reset so that the checkboxes are cleared for the next run
            request.session['selected_items'] = ''

            # Finally run the galaxy workflow!!
            run_galaxy_workflow(wr.workflow.id, request.user, wr.workflow.galaxyinstancetracking,
                                pkd, l, wr.history_name, wr.library)

            # Show the progress of all the workflows running (including the one we have just started)

            return redirect(self.redirect_to)


        return render(request, self.template_name, {'form': form, 'list': l, 'wid':self.kwargs['wid']})


class WorkflowStatus(LoginRequiredMixin, View):
    '''
    View available Galaxy. If any new workflows are added to a Galaxy instance the user should sync first before
    they can be seen in the table.
    '''

    # template_name = 'galaxy/status.html'

    def get(self, request, *args, **kwargs):
        data = get_workflow_status(request.user)

        table = WorkflowStatusTable(data)

        return render(request, 'galaxy/workflow_status.html', {'table':table})

    def post(self, request, *args, **kwargs):
        workflow_sync(request.user)
        # redirects to show the current available workflows
        return redirect('workflow_summary')

class HistoryDataBioBlendListView(LoginRequiredMixin, View):


    def get(self, request, *args, **kwargs):
        data = get_history_data(self.kwargs['pk'], request.user)

        table = HistoryDataTable(data)

        return render(request, 'galaxy/history_data_bioblend_list.html', {'table': table})
        # return render(request, 'galaxy/history_status.html', {'table': table})


class HistoryDataCreateView(LoginRequiredMixin, CreateView):

    model = HistoryData
    success_url = '/galaxy/success'
    form_class = HistoryDataForm

    def get_initial(self):


        user = self.request.user


        history_internal_id = self.kwargs.get('history_internal_id')
        history_data_galaxy_id = self.kwargs.get('galaxy_id')
        history_d = init_history_data_save_form(user, history_internal_id, history_data_galaxy_id)

        return {'history': history_internal_id,
                'name': history_d['name'] }

    def save_form(self, form):
        history_data_obj = form.save(commit=False)
        history_data_obj.user = self.request.user

        history_internal_id = self.kwargs.get('history_internal_id')
        history_data_galaxy_id = self.kwargs.get('galaxy_id')

        return history_data_save_form(self.request.user, history_internal_id, history_data_galaxy_id, history_data_obj)



    def form_valid(self, form):
        self.save_form(form)
        return render(self.request, 'gfiles/submitted.html')



class HistoryListView(LoginRequiredMixin, TableFileSelectMixin,SingleTableMixin, ExportMixin, FilterView):
    '''
    View and initiate a run for all registered workflows.

    Workflows can also be synced here as well
    '''
    table_class = HistoryTable
    model = History
    filterset_class = HistoryFilter
    form_class = DeleteGalaxyHistoryForm
    template_name = 'galaxy/history_status.html'
    table_pagination = {"per_page": 50}
    initial_context = {'library': True,
                       'django_url': '/galaxy/history_status/',
                       'django_update_url': '/galaxy/history_status_update/'}



    def get(self, request, *args, **kwargs):
        # we have to overide the standard get to add some extra information to the context

        form = self.form_class()
        context = self.form2context(form)

        return render(request, self.template_name, context=context)

    def form_valid(self, request, form):

        pks = request.POST.getlist("check")

        delete_galaxy_histories(pks, purge=form.cleaned_data['purge'], user=request.user)
        return render(request, 'gfiles/submitted.html')



def history_status_update(request):
    data = get_history_status(request.user)
    return JsonResponse({'table_data':data})


def workflow_status_update(request):

    data = get_workflow_status(request.user)
    return JsonResponse({'table_data':data})




class WorkflowCreateView(LoginRequiredMixin, CreateView):

    model = Workflow
    form_class = WorkflowForm
    success_url = '/galaxy/success'

    def form_valid(self, form):
        user = self.request.user
        w = form.save(commit=False)
        w.added_by = user
        w.save()
        w.save_related()

        return super(WorkflowCreateView, self).form_valid(form)

    def get_initial(self):
        return {'galaxyinstancetracking':GalaxyInstanceTracking.objects.last()}

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super(WorkflowCreateView, self).get_form_kwargs(**kwargs)
        form_kwargs["user"] = self.request.user
        return form_kwargs


def checkbox_selected(request):
    selected = request.session['selected']
    return JsonResponse({'selected': selected})






def selected_items_2_pks(selected_items):
    pkd = {}
    for k, v in six.iteritems(selected_items):
        if v:
            kl = k.split('_')
            table_id = kl[0]
            pk = kl[1]
            if not table_id in pkd:
                pkd[table_id] = []
            pkd[table_id].append(pk)
    return pkd


def ajax_post_selected(request):
    # request dictionary
    rd = json.loads(request.body)

    if 'selected_items' in request.session and request.session['selected_items']:
        # session dictionary
        # if isinstance(request.session['selected_items'], str) or isinstance(request.session['selected_items'], unicode):
        sd = json.loads(request.session['selected_items'])
        # else:
        #     sd = request.session['selected_items']


        for k, v in six.iteritems(rd['selected_items']):
            sd[k] = v

        request.session['selected_items'] = json.dumps(sd)
    else:
        request.session['selected_items'] = json.dumps(rd['selected_items'])

    return request

def success(request):
    return render(request, 'galaxy/success.html')



