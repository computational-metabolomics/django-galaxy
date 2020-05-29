from __future__ import print_function
import os
from ftplib import FTP
from past.builtins import xrange
from pathlib import Path

from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.libraries import LibraryClient
from bioblend.galaxy.tools import ToolClient
from bioblend.galaxy.histories import HistoryClient

from django.db.models.query import QuerySet
from django.conf import settings

from gfiles.models import GenericFile

from galaxy.models import GalaxyFileLink, GalaxyUser
from galaxy.utils.sync_files import sync_galaxy_files
from galaxy.utils.galaxy_utils import get_gi_gu, create_library, get_time_stamp

def f2dl_action(gfile_ids, f2dl_param, galaxy_pass):

    # get selected files
    selected_files = GenericFile.objects.filter(pk__in=gfile_ids)
    galaxy_folder = f2dl_param.folder_name

    # get the Galaxy Bioblend clients
    git = f2dl_param.galaxyinstancetracking
    gi, gu = get_gi_gu(f2dl_param.added_by, git)

    lc = LibraryClient(gi)

    # Create base library (just output the lib bioblend object if already created)
    lib = create_library(lc, f2dl_param.added_by.username)

    # get full paths from database
    filelist = files2paths(selected_files)
    if not filelist:
        print('filelist empty')
        return []

    # Create the folders in Galaxy data library (can be nested if user used forward slashses)
    folders = galaxy_folder.split('/')
    folder_id = create_folders(lc, lib['id'], base_f_id=None, folders=folders)
    lib_id = lib['id']

    # upload the files to the folder
    uploaded_files = add_filelist_datalib(filelist,
                                          f2dl_param,
                                          lc,
                                          gu,
                                          gi,
                                          galaxy_pass,
                                          lib_id,
                                          folder_id,
                                          galaxy_folder)

    # link files to django database
    link_files_in_galaxy(uploaded_files, selected_files, git, library=True)

    # check purged files are reference in the database correctly
    sync_galaxy_files(f2dl_param.added_by)



def files2paths(mfiles):
    return [os.path.join(settings.MEDIA_ROOT, f.data_file.name) for f in mfiles]


def create_folders(lc, libid, base_f_id, folders):
    # Recursively create folders until all folders have been created
    if not folders:
        return base_f_id

    f = folders.pop(0)
    gf = lc.create_folder(libid, f, base_folder_id=base_f_id)
    return create_folders(lc=lc, libid=libid, base_f_id=gf[0]['id'], folders=folders)


def add_filelist_datalib(filelist, f2dl_param, lc, gu, gi,
                         galaxy_pass, lib_id, folder_id, history_ftp_name=''):
    # add a filelist to datalib, either with ftp method or through directory method
    if f2dl_param.ftp:
        history_files = add_filelist_to_history_via_ftp(filelist, gu, gi,
                                                        galaxy_pass, f2dl_param, history_ftp_name)
        data_lib_files = copy_history_files_to_datalib(history_files, lc, lib_id, folder_id)
    else:

        data_lib_files = add_files_2_galaxy_datalib_dir(lc=lc,
                                                        lib_id=lib_id,
                                                        filelist=filelist,
                                                        folder_id=folder_id,
                                                        link2files=f2dl_param.link2files)
    return data_lib_files


def add_filelist_to_history_via_ftp(filelist, gu, gi, galaxy_pass,
                                    galaxy_isa_upload_param, full_assay_name):
    git = galaxy_isa_upload_param.galaxyinstancetracking
    # get the study name of the group and create folder

    #
    # print 'ftp_host and port', git.ftp_host, git.ftp_port, gu.email, galaxy_pass
    send_to_ftp(filelist, host=git.ftp_host, port=git.ftp_port, user=gu.email, password=galaxy_pass)

    uploaded_files, hist = transfer_filelist_from_ftp(gi, filelist, history_name=full_assay_name)

    return uploaded_files

def send_to_ftp(filelist, host, port, user, password):
    ftp = FTP()
    # parsed = urlparse(host)
    # ftp.connect(parsed.netloc, port)

    ftp.connect(host, port)
    ftp.login(user=user, passwd=password)

    for file in filelist:
        print(file)
        fn = os.path.basename(file)
        with open(file, 'rb') as f:
            ftp.storbinary('STOR {}'.format(fn), f)

    ftp.close()


def transfer_filelist_from_ftp(gi, filelist, history_name):

    tc = ToolClient(gi)
    hc = HistoryClient(gi)

    st = get_time_stamp()
    hist = hc.create_history('{}-{}'.format(history_name, st))

    uploaded_files = []
    for f in filelist:
        upf = tc.upload_from_ftp(path=os.path.basename(f), history_id=hist['id'])['outputs'][0]
        print(upf)
        uploaded_files.append(upf)
    return uploaded_files, hist


def copy_history_files_to_datalib(history_files, lc, lib_id, folder_id):
    
    return [lc.copy_from_dataset(lib_id, f['id'], folder_id) for f in history_files]



def add_files_2_galaxy_datalib_dir(lc, lib_id, folder_id, filelist,
                                   local_path=False, link2files=True):
    all_uploaded_files = []
    filelist = [os.path.abspath(Path(f).resolve()) for f in filelist]

    if local_path:
        for f in filelist:
            f = Path(f).resolve()
            all_uploaded_files.append(lc.upload_file_from_local_path(lib_id,
                                                                     f,
                                                                     folder_id=folder_id,
                                                                     file_type='auto'))
        return all_uploaded_files
    else:
        filechunks = get_filechunks_dtypes(filelist)
        for filechunk in filechunks:
        
            if isinstance(filechunk, list):
                filelist_str = '\n'.join(filechunk)
            else:
                filelist_str = filechunk

            if link2files:
                link_data_only = 'link_to_files'
            else:
                link_data_only = None

            # Check for file types (only need to check one file as if
            # mzml or raw they should be the same file type in each
            # chunk
            if '.mzml' in filechunk[0].lower():
                file_type = 'mzml'
            elif '.raw' in filechunk[0].lower():
                file_type = 'thermo.raw'
            else:
                file_type = 'auto'

            print(lib_id, filelist_str, folder_id,link_data_only, file_type)

            uploaded_files = lc.upload_from_galaxy_filesystem(lib_id,
                                                              filelist_str,
                                                              folder_id=folder_id,
                                                              file_type=file_type,
                                                              link_data_only=link_data_only,
                                                              tag_using_filenames=False)

            all_uploaded_files.extend(uploaded_files)

        return all_uploaded_files


def link_files_in_galaxy(uploaded_files, filedetails, git, galaxy_library=True):

    if isinstance(filedetails[0], dict):
        selected_ids = {f['original_filename']: f['id'] for f in filedetails}
    else:
        selected_ids = {f.original_filename: f.id for f in filedetails}

    gfls = []
    for i in range(0, len(uploaded_files)):
        print(uploaded_files[i])
        if len(gfls) % 10 == 0:
            print(gfls)
            GalaxyFileLink.objects.bulk_create(gfls)
            gfls = []
            
        gfls.append(GalaxyFileLink(galaxy_library=galaxy_library,
                                   galaxy_id=uploaded_files[i]['id'],
                                   genericfile_id=selected_ids[uploaded_files[i]['name']],
                                   galaxyinstancetracking=git))

    print('CHECK', gfls)
    GalaxyFileLink.objects.bulk_create(gfls)


def f2h_action(gfile_ids, f2h, galaxy_pass):
    selected_files = GenericFile.objects.filter(pk__in=gfile_ids)
    history_name = f2h.history_name
    git = f2h.galaxyinstancetracking
    user = f2h.added_by
    filelist = files2paths(selected_files)

    if not filelist:
        print('filelist empty')
        return []

    gu = GalaxyUser.objects.get(internal_user=user, galaxyinstancetracking=git)
    api_key = gu.api_key
    galaxy_url = git.url
    gi = GalaxyInstance(galaxy_url, key=api_key)
    gi.verify=False

    filelist = files2paths(selected_files)
    print('ftp_host and port', git.ftp_host, git.ftp_port, gu.email, galaxy_pass)
    send_to_ftp(filelist, host=git.ftp_host, port=git.ftp_port, user=gu.email, password=galaxy_pass)

    uploaded_files, hist = transfer_filelist_from_ftp(gi, filelist, history_name=history_name)
    link_files_in_galaxy(uploaded_files, selected_files, git, library=False)


def get_filechunks_dtypes(filelist):
    raw_files = []
    mzml_files = []
    other_files = []
    
    for f in filelist:
        if '.mzml' in f.lower():
            mzml_files.append(f)   
        elif '.raw' in f.lower():
            raw_files.append(f)
        else:
            other_files.append(f)
    all = []

    all.extend(get_filechunks(mzml_files))
    all.extend(get_filechunks(raw_files))
    all.extend(get_filechunks(other_files))
    return all

def get_filechunks(filelist):
    
    if len(filelist) >= 5:
        return [filelist[x:x + 5] for x in xrange(0, len(filelist), 5)]
    else:
        return filelist



