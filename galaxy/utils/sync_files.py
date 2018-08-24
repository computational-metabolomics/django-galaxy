from __future__ import print_function
from bioblend.galaxy.datasets import DatasetClient
from bioblend.galaxy.libraries import LibraryClient

from galaxy.models import GalaxyInstanceTracking, GalaxyFileLink
from galaxy.utils.galaxy_utils import get_gi_gu


def sync_galaxy_files(user):
    print('check')
    # go through all the galaxylink files associated with the galaxy_instance_id
    gits = GalaxyInstanceTracking.objects.filter(galaxyuser__internal_user=user)

    # loop through galaxy instance
    for git in gits:
        print(git, 'GIT..................................')
        gflks = GalaxyFileLink.objects.filter(galaxyinstancetracking=git)

        gi, gu = get_gi_gu(user, git)
        # loop through galaxy files
        for gflk in gflks:
            dc = DatasetClient(gi)
            lc = LibraryClient(gi)

            if gflk.galaxy_library:

                mtch = dc.show_dataset(gflk.galaxy_id, hda_ldda='lda')
                print('MATCH', mtch)
                if isinstance(mtch, dict):
                    if mtch['deleted']:
                        gflk.removed = True

                else:
                    gflk.removed = True


            else:
                mtch = dc.show_dataset(gflk.galaxy_id, hda_ldda='hda')
                if isinstance(mtch, dict) and (mtch['deleted'] or mtch['purged']):
                    gflk.removed=True

            gflk.save()
