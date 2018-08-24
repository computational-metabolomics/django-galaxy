from __future__ import print_function
import json
import os
import time
import random
import string
from datetime import datetime

from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.histories import HistoryClient
from bioblend.galaxy.workflows import WorkflowClient

from gfiles.models import GenericFile

from galaxy.models import Workflow, GalaxyUser, GalaxyInstanceTracking, WorkflowInput
from galaxy.utils.upload_to_galaxy import get_time_stamp, get_gi_gu


def workflow_sync(user):

    # get all instances for that user
    gits = GalaxyInstanceTracking.objects.filter(galaxyuser__internal_user=user)
    dj_wfs = Workflow.objects.all()
    # loop through instances
    all_wfs = []
    for git in gits:
        ## loop through workflows for that instance
        gi, gu = get_gi_gu(user, git)
        wc = WorkflowClient(gi)
        wfs = wc.get_workflows()
        all_wfs.extend(wfs)
        for wf in wfs:
            wfd = wc.show_workflow(wf['id'])
            ### check if id of the workflow already in galaxy
            wjson = wc.export_workflow_json(wf['id'])

            dj_wf = dj_wfs.filter(galaxy_id=wfd['id'])
            if dj_wf:
                if not dj_wf[0].latest_workflow_uuid == wf['latest_workflow_uuid']:
                    dj_wf_update = dj_wf[0]
                    dj_wf_update.latest_workflow_uuid = wf['latest_workflow_uuid']
                    dj_wf_update.name = wf['name']
                    dj_wf_update.workflowjson = wjson
                    dj_wf_update.save()
            else:
                workflow = Workflow(galaxy_id=wf['id'], name=wf['name'], description='added automatically',
                         galaxyinstancetracking=git, added_by=user, workflowjson=wjson)
                workflow.save()

    all_wfs_gi = [w['id'] for w in all_wfs]

    ## check if workflow is currently accessible
    Workflow.objects.exclude(galaxy_id__in=all_wfs_gi).update(accessible=False)

def random_string(n):
    # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def get_workflow_status(user):
    # go through every galaxy instance
    gits = GalaxyInstanceTracking.objects.filter(galaxyuser__internal_user=user)
    dj_wfs = Workflow.objects.all()
    # loop through instances
    status = []
    for git in gits:
        ## loop through workflows for that instance
        gi, gu = get_gi_gu(user, git)
        wc = WorkflowClient(gi)
        hc = HistoryClient(gi)
        wfs = wc.get_workflows()
        for wf in wfs:
            wfd = wc.show_workflow(wf['id'])
            winvoke = wc.get_invocations(wf['id'])
            for wi in winvoke:
                wid = wc.show_invocation(wf['id'], wi['id'])
                h_l = hc.get_histories(wid['history_id'], deleted=True)

                if h_l:
                    h = h_l[0]
                else:
                    continue
                sd = get_status_d(wid)
                sd['name'] = wfd['name']
                hd = hc.show_history(h['id'])
                sd['history_name'] = h['name']
                datetime_object = datetime.strptime(hd['update_time'], '%Y-%m-%dT%H:%M:%S.%f')
                # sd['history_url'] =  '{}{}'.format(git.url, hd['url'])

                sd['update_time'] =  datetime_object.strftime('%Y-%m-%d %H:%M:%S')
                sd['update_time_unix'] = unixtime(datetime_object)
                sd['galaxy_instance'] = git.name
                status.append(sd)

    status = sorted(status, key=lambda k: k['update_time_unix'], reverse=True)

    return status

def unixtime(d):
    return time.mktime(d.timetuple())


def get_status_d(wid):

    d = {}
    d['finished_tasks'] = 0
    d['na'] = 0
    d['todo_tasks'] = 0
    d['running_tasks'] = 0
    d['failed_tasks'] = 0
    d['paused_tasks'] = 0

    rtn = []
    for wd in wid['steps']:
        if wd['state']=='ok':
            d['finished_tasks']+=1
        elif wd['state']=='running':
            d['running_tasks']+=1
            rtn.append(wd['workflow_step_label'])
        elif wd['state']=='new':
            d['todo_tasks']+=1
        elif wd['state']==None:
            d['na'] += 1
        elif wd['state']=='paused':
            d['paused_tasks'] += 1
        elif wd['state']=='error':
            d['failed_tasks'] += 1

    d['running_tasks_names'] = ', '.join([str(e) for e in rtn])

    total = d['running_tasks'] + d['todo_tasks'] + d['finished_tasks'] + d['failed_tasks'] + d['paused_tasks']

    if total==0:
        d['estimated_progress'] = 0
    else:
        d['estimated_progress'] = round(d['finished_tasks']/float(total) *100.0, )

    return d


def run_galaxy_workflow(wid, user, git, pkd, l, history_name, library):

    gi, gu = get_gi_gu(user, git)

    st = get_time_stamp()

    workflow_input_d = get_workflow_inputs(l, pkd, gi, git, history_name, library)

    wc = WorkflowClient(gi)
    print(workflow_input_d)
    workflow = Workflow.objects.get(id=wid)

    wf = wc.get_workflows(workflow_id=workflow.galaxy_id)[0]

    print('CHECK CHECK', wf)

    wfi = wc.invoke_workflow(wf['id'], inputs=workflow_input_d,
                       import_inputs_to_history=True, history_name='{}_({})'.format(history_name, st))


    return wfi


def get_workflow_inputs(l, pkd, gi, git, history_name, library):
    # LibraryDatasetDatasetAssociation (ldda), LibraryDataset (ld), HistoryDatasetAssociation (hda),
    # or HistoryDatasetCollectionAssociation (hdca).
    st = get_time_stamp()

    hc = HistoryClient(gi)
    worklow_inputs_d = {}

    for table, filter, dinput_name, dinput_step, dinput_type in l:
        pks = pkd[str(table.prefix)]
        print('PKS before ', pks)
        #  will get multiple inputs here because we can multiple galaxyfilelinks per file. They are all the same
        # file so we can just get unique
        selected_objects = GenericFile.objects.filter(
            pk__in=pks
        ).distinct()

        print('PKS', pks, dinput_type)
        print(selected_objects)

        if dinput_type=='data_input':
            print('DATA INPUT')
            # can only use the first selection (need to use data collection for multiple files, currently this
            # approach doesn't support using 'multiple files' as input as not possible with BioBlend (i think)
            s = selected_objects[0]
            gid = s.galaxyfilelink_set.filter(galaxy_library=library)[0].galaxy_id

            print(gid)

            worklow_inputs_d[dinput_step] = {'id':gid, 'src':'ld'}

        elif dinput_type == 'data_collection_input':
            print('DATA INPUT COLLECTION')
            element_identifiers = []
            hist = hc.create_history('{}-(data-history-{})-{}'.format(history_name, dinput_name, st))


            for s in selected_objects:
                print(s)
                gfl = s.galaxyfilelink_set.filter(galaxy_library=library)[0]

                if library:
                    dataset = hc.upload_dataset_from_library(hist['id'], lib_dataset_id=gfl.galaxy_id)
                    element_identifiers.append({'id': dataset['id'],
                                                'name': os.path.basename(dataset['file_name']),
                                                'src': 'hda'})
                else:
                    element_identifiers.append({'id': gfl.galaxy_id,
                                                'name': gfl.genericfile.data_file.name,
                                                'src': 'hda'})

            c_descript = {'collection_type': 'list',
                          'element_identifiers': element_identifiers,
                          'name': dinput_name,}

            dc = hc.create_dataset_collection(hist['id'], c_descript)
            worklow_inputs_d[dinput_step] = {'id':dc['id'], 'src': 'hdca'}

    return worklow_inputs_d


def check_workflow_data_inputs(wid, wc):
    wjson = wc.export_workflow_json(wid)
    steps = wjson['steps']
    data_inputs = []
    for step, details, in steps.iteritems():
        print('DETAILS', details)
        dtype = details['type']
        name = details['label']
        if dtype == 'data_input' or dtype == 'data_collection_input':
            data_inputs.append({'step':step, 'dtype':dtype, 'name': name})

    return data_inputs



def get_galaxy_workflow_inputs(w, user):
    wf = w.workflowfile
    git = w.galaxyinstancetracking
    wf_name = w.name

    api_key = GalaxyUser.objects.get(internal_user=user, galaxyinstancetracking=git).api_key
    galaxy_url = git.url

    gi = GalaxyInstance(galaxy_url, key=api_key)
    gi.verify = False
    wc = WorkflowClient(gi)
    wfd = wf.read()

    jsonload = json.loads(wfd)

    now = datetime.datetime.now()

    jsonload['name'] = '{} dj-upload[{} {}]'.format(jsonload['name'], wf_name,
                                                    now.strftime("%Y-%m-%d"))

    wfimp = wc.import_workflow_json(jsonload)

    return check_workflow_data_inputs(wfimp['id'], wc), wfimp['id']



def save_new_workflow(form, user):

    w = form.save(commit=False)
    w.added_by = user
    w.save()

    data_inputs, w_gid = get_galaxy_workflow_inputs(w, user)
    w.galaxy_id = w_gid
    w.save()

    WorkflowInput.objects.bulk_create(
        [WorkflowInput(step=d['step'], datatype=d['dtype'], name=d['name'], workflow=w) for d in data_inputs]
    )




