import django_tables2 as tables
from galaxy.models import Workflow, History
from django_tables2.export.views import ExportMixin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_tables2_column_shifter.tables import ColumnShiftTable
from django_tables2.utils import A


import os



class ProgressColumn(tables.Column):
    def render(self, value):
        return format_html('<div class="progress">'
                           '    <div class="progress-bar" role="progressbar" aria-valuenow={} aria-valuemin="0" aria-valuemax="100" style="width:{}%">'
                           '         {}%'
                           '    </div>'
                           '</div>', value, value, value)


class WorkflowStatusTable(ColumnShiftTable):
    galaxy_instance = tables.Column()
    name = tables.Column()
    update_time = tables.Column()
    history_name = tables.Column()
    # history_url = tables.URLColumn(text='history log')
    finished_tasks = tables.Column()
    todo_tasks = tables.Column()
    running_tasks = tables.Column()
    paused_tasks = tables.Column()
    failed_tasks = tables.Column()
    # running_tasks_details = tables.Column()
    estimated_progress = ProgressColumn()

    # check = tables.CheckBoxColumn(accessor="name",
    #                                        attrs={
    #                                            "th__input": {"onclick": "toggle(this)"},
    #                                            "td__input": {"onclick": "addfile(this)"}},
    #                                        )

    class Meta:
        attrs = {'class': 'paleblue', 'id':'status_table'}
        template = 'django_tables2/bootstrap.html'


class HistoryDataTable(ColumnShiftTable):
    galaxy_instance_id = tables.Column()
    galaxy_instance = tables.Column()

    accessible = tables.Column()
    annotation = tables.Column()
    create_time = tables.Column()
    creating_job = tables.Column()
    data_type = tables.Column()
    dataset_id = tables.Column()
    deleted = tables.Column()
    download_url = tables.Column()
    extension = tables.Column()
    file_ext = tables.Column()
    file_name = tables.Column()
    file_size = tables.Column()
    hda_ldda = tables.Column()
    history_content_type = tables.Column()
    history_id= tables.Column()
    id = tables.Column()
    model_class = tables.Column()
    name = tables.Column()
    purged = tables.Column()
    rerunnable = tables.Column()
    state = tables.Column()
    type = tables.Column()
    update_time = tables.Column()
    url = tables.Column()
    uuid = tables.Column()
    visible = tables.Column()
    history_internal_id = tables.Column()


    history_data_create = tables.LinkColumn('history_data_create', verbose_name='Save history data item',
                                            text='Save item', args=[A('history_internal_id'), A('id')])


    class Meta:
        attrs = {'class': 'paleblue'}
        template = 'django_tables2/bootstrap.html'

    def get_column_default_show(self):
        self.column_default_show = ['galaxy_instance', 'name', 'data_type', 'create_time', 'download_url']
        return super(HistoryDataTable, self).get_column_default_show()






class HistoryTable(ColumnShiftTable):
    # export_formats = ['csv', 'xls']
    history_data_bioblend_list = tables.LinkColumn('history_data_bioblend_list', text='View data', args=[A('id')])

    check = tables.CheckBoxColumn(accessor="pk",
                                  attrs={
                                      "th__input": {"onclick": "toggle(this)"},
                                      "td__input": {"onclick": "addfile(this)"}},
                                  )



    def render_estimated_progress(self, value):
        return format_html('<div class="progress">'
                           '    <div class="progress-bar" role="progressbar" aria-valuenow={} aria-valuemin="0" aria-valuemax="100" style="width:{}%">'
                           '         {}%'
                           '    </div>'
                           '</div>', value, value, value)

    def get_column_default_show(self):
        self.column_default_show = ['galaxy_instance', 'name', 'update_time', 'accessible', 'running', 'estimated_progress', 'history_data_list', 'check']
        return super(HistoryTable, self).get_column_default_show()


    class Meta:
        model = History

        attrs = {
            ' class ': 'paleblue',
        }
        # running_tasks_details = tables.Column()
        order_by = ('-update_time',)

        template = 'django_tables2/bootstrap.html'




class WorkflowTable(ColumnShiftTable):
    run = tables.LinkColumn('runworkflow', text='run', args=[A('id')])

    def get_column_default_show(self):
        self.column_default_show = ['id', 'name', 'galaxyinstancetracking', 'accessible', 'run']
        return super(WorkflowTable, self).get_column_default_show()

    class Meta:

        model = Workflow
        attrs = {'class': 'paleblue'}
        template = 'django_tables2/bootsrap.html'