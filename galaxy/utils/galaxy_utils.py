from __future__ import print_function
import datetime
import time
from bioblend.galaxy import GalaxyInstance
from galaxy.models import GalaxyUser


def get_gi_gu(user, git):
    gu = GalaxyUser.objects.get(internal_user=user, galaxyinstancetracking=git)

    galaxy_url = git.url
    gi = GalaxyInstance(galaxy_url, key=gu.api_key)
    gi.verify = False

    return gi, gu


def create_library(lc, name='mogi'):
    # Create base library (just output the lib bioblend object if already created)
    current_mogi = lc.get_libraries(name=name)
    if current_mogi:
        lib = current_mogi[0]
        if len(current_mogi) > 1:
            print('More than 1 library with {} name, using library for'.format(name), lib)
    else:
        lib = lc.create_library(name='mogi')
    return lib


def get_time_stamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')