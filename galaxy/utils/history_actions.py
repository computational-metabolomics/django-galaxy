from __future__ import print_function
import time
import random
import string
import os

import sys

if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from urllib import urlretrieve


from datetime import datetime
import requests
from bioblend.galaxy.histories import HistoryClient
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from galaxy.models import GalaxyInstanceTracking, History
from galaxy.utils.upload_to_galaxy import get_gi_gu
from gfiles.utils.save_as_symlink import save_as_symlink
from django.conf import settings

def random_string(n):
    # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def get_history_status(user):
    # go through every galaxy instance
    gits = GalaxyInstanceTracking.objects.filter(galaxyuser__internal_user=user)

    # loop through instances
    status = []
    for git in gits:
        ## loop through workflows for that instance
        gi, gu = get_gi_gu(user, git)
        hc = HistoryClient(gi)
        hists = hc.get_histories()

        # loop through and create a list of dictionaries for our django table
        for hist in hists:
            print(hist)
            sd = {}
            # add useful info
            history_info = hc.show_history(hist['id'])

            # add status info
            sd_bioblend = hc.get_status(hist['id'])
            state_details = sd_bioblend['state_details']
            sd.update(state_details)

            sd['estimated_progress'] = sd_bioblend['percent_complete']
            datetime_object = datetime.strptime(history_info['update_time'], '%Y-%m-%dT%H:%M:%S.%f')
            sd['update_time'] = datetime_object.strftime('%Y-%m-%d %H:%M:%S')
            sd['update_time_unix'] = unixtime(datetime_object)
            sd['galaxy_instance'] = git.name

            sd['name'] = hist['name']

            hsq = History.objects.filter(galaxy_id=hist['id'], galaxyinstancetracking=git)

            if hsq:

                hs = hsq[0]
                hs.name = hist['name']
                hs.update_time = datetime_object.strftime('%Y-%m-%d %H:%M:%S')
                hs.empty = state_details['empty']
                hs.error = state_details['error']
                hs.failed_metadata = state_details['failed_metadata']
                hs.new = state_details['new']
                hs.ok = state_details['ok']
                hs.paused = state_details['paused']
                hs.running = state_details['running']
                hs.queued = state_details['queued']
                hs.setting_metadata = state_details['setting_metadata']
                hs.upload = state_details['upload']
                hs.estimated_progress = sd_bioblend['percent_complete']
            else:
                hs = History(galaxyinstancetracking=git,
                               name=hist['name'],
                               update_time=datetime_object.strftime('%Y-%m-%d %H:%M:%S'),
                               empty=state_details['empty'],
                               error=state_details['error'],
                               failed_metadata=state_details['failed_metadata'],
                               new=state_details['new'],
                               ok=state_details['ok'],
                               paused=state_details['paused'],
                               running=state_details['running'],
                               queued=state_details['queued'],
                               setting_metadata=state_details['setting_metadata'],
                               upload=state_details['upload'],
                               galaxy_id=hist['id'],
                               estimated_progress = sd_bioblend['percent_complete']
                               )

            hs.save()
            sd['history_data_bioblend_list'] = '/galaxy/history_data_bioblend_list/{}'.format(hs.pk)
            status.append(sd)


    status = sorted(status, key=lambda k: k['update_time_unix'], reverse=True)

    return status

def unixtime(d):
    return time.mktime(d.timetuple())


def delete_galaxy_histories(pks, purge, user):
    hss = History.objects.filter(pk__in=pks)

    for hs in hss:
        git = hs.galaxyinstancetracking
        gi, gu = get_gi_gu(user, git)
        hc = HistoryClient(gi)
        hc.delete_history(hs.galaxy_id, purge)
        hs.delete()


def get_history_data(pk, user, name_filter=None, data_type=None):
    hs = History.objects.get(pk=pk)
    git = hs.galaxyinstancetracking
    gi, gu = get_gi_gu(user, git)
    hc = HistoryClient(gi)
    hdatasets = hc.show_matching_datasets(hs.galaxy_id)

    if data_type:
        hdatasets = [h for h in hdatasets if h['extension'] in data_type]

    if name_filter:
        hdatasets = [h for h in hdatasets if h['name'] in name_filter]

    for h in hdatasets:
        h['galaxy_instance'] = git.name
        h['galaxy_instance_id'] = git.pk
        h['history_internal_id'] = pk

    return hdatasets


def history_data_save_form(user, history_internal_id, galaxy_dataset_id, history_data_obj):
    history_d = init_history_data_save_form(user, history_internal_id, galaxy_dataset_id)

    # If we can access the file from Galaxy directly we won't download
    print('history d', history_d)
    if history_d['abs_pth']:
        history_data_obj = save_as_symlink(history_d['abs_pth'], history_d['name'], history_data_obj)

    else:
        # data_pth = urlretrieve(history_d['full_download_url'])[0]
        response = requests.get(history_d['full_download_url'])
        data_file = SimpleUploadedFile(history_d['name'], response.content)
        history_data_obj.data_file = data_file

        # history_data_obj.data_file.save(history_d['name'], SimpleUploadedFile(data_pth))
        history_data_obj.save()


    return history_data_obj


def init_history_data_save_form(user, history_internal_id, galaxy_dataset_id):
    print(user)
    h = History.objects.get(pk=history_internal_id)

    gi, gu = get_gi_gu(user, h.galaxyinstancetracking)

    # save temp history object
    hc = HistoryClient(gi)

    history_d = hc.show_dataset(history_id=h.galaxy_id, dataset_id=galaxy_dataset_id)

    history_d['full_download_url'] = h.galaxyinstancetracking.url + history_d['download_url']

    history_d['abs_pth'] = ''

    data_pth = history_d['file_name'].replace('/export/', '')
    fullpth = os.path.join(h.galaxyinstancetracking.galaxy_root_path, data_pth)

    if os.path.exists(fullpth):
         history_d['abs_pth'] = fullpth

    return history_d






