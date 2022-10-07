# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
#  python manage.py test misa -v 3 --keepdb
#  coverage run --source='.' manage.py test galaxy -v 3 --keepdb
#  coverage report
#  coverage html --omit="admin.py"

import subprocess
import os
import requests

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

from django.contrib.auth.models import AnonymousUser, User

from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from galaxy.views import GalaxyInstanceCreateView, GalaxyUserCreateView, GalaxySync,\
    WorkflowListView, GenericFilesToGalaxyHistory, FilesToGalaxyDataLib
from galaxy.models import GalaxyInstanceTracking, GalaxyUser, Workflow, WorkflowInput, GalaxyFileLink
from galaxy.utils.galaxy_utils import get_gi_gu
from bioblend.galaxy.workflows import WorkflowClient
from bioblend.galaxy import GalaxyInstance

def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def add_middleware_to_response(response, middleware_class):
    middleware = middleware_class()
    middleware.process_response(response)
    return response

def add_message_and_session_middleware_to_request(request):
    request = add_middleware_to_request(request, SessionMiddleware)
    request = add_middleware_to_request(request, MessageMiddleware)
    request.session.save()
    return request

def add_message_and_session_middleware_to_response(response):
    response = add_middleware_to_request(response, SessionMiddleware)
    response = add_middleware_to_request(response, MessageMiddleware)
    response.session.save()
    return response


def setup_galaxy():
    try:
        request = requests.get('http://127.0.0.1:9090')
        if request.status_code == 200:
            return 0
    except requests.exceptions.ConnectionError as e:
        print(e)

    docker_run = """
        docker run -d -p 9090:80 -p 9022:22 -p 9021:21 \
            -e GALAXY_CONFIG_ADMIN_USERS=jacob@jacob.com \
            -e GALAXY_CONFIG_ALLOW_USER_CREATION=True \
            -e GALAXY_CONFIG_LIBRARY_IMPORT_DIR=True \
            -e GALAXY_CONFIG_USER_LIBRARY_IMPORT_DIR=True \
            -e GALAXY_CONFIG_ALLOW_LIBRARY_PATH_PASTE=True \
            -e GALAXY_CONFIG_CONDA_ENSURE_CHANNELS=tomnl,iuc,bioconda,conda-forge,defaults,r \
            workflow4metabolomics/galaxy-workflow4metabolomics
        """
    print(docker_run)
    subprocess.call(docker_run, shell=True)

    import time
    timeout = time.time() + 60 * 5  # 5 minutes from now
    while True:

        if time.time() > timeout:
            break
        else:
            try:
                request = requests.get('http://127.0.0.1:9090')
                if request.status_code == 200:
                    break
                else:
                    print('Web site does not exist yet')
            except requests.exceptions.ConnectionError as e:
                print(e)
        time.sleep(5)


class GalaxyInstanceCreateTestCase(TestCase):
    urls = 'galaxy.test_urls'
    def setUp(self):
        setup_galaxy()
        self.factory = RequestFactory()
        User = get_user_model()
        # Should only be admin that can use the galaxy interface
        self.user = User.objects.create_superuser(username='jacob', email='jacob@jacob.com',
                                             password='top_secret'
                                             )

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/add_galaxy_instance/')

        request.user = AnonymousUser()
        request = add_message_and_session_middleware_to_request(request)

        response = GalaxyInstanceCreateView.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        # Should redirect and just send a message that user does not have permissions (unsure how you could test
        # the message on a redirect response though)
        self.assertRedirects(response, '/galaxy/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('add_galaxy_instance'))
        request.user = self.user

        request = add_message_and_session_middleware_to_request(request)

        response = GalaxyInstanceCreateView.as_view()(request)

        print(response)

        self.assertEqual(response.status_code, 200)


    def test_post_valid_url(self):
        """
        Test post with valid url
        """
        git_before = len(GalaxyInstanceTracking.objects.all())

        self.client.force_login(self.user)
        response = self.client.post('/galaxy/add_galaxy_instance/',
                                    {'url': 'http://127.0.0.1:9090',
                                     'name': 'test_local',
                                     'ftp_host': 'http://127.0.0.1',
                                     'ftp_port': '9021'})

        self.assertEqual(response.status_code, 302) # redirected page (e.g. success page)
        self.assertEqual(GalaxyInstanceTracking.objects.last().url,  'http://127.0.0.1:9090')
        self.assertEqual(GalaxyInstanceTracking.objects.last().name, 'test_local')
        self.assertEqual(GalaxyInstanceTracking.objects.last().ftp_host, 'http://127.0.0.1')
        self.assertEqual(GalaxyInstanceTracking.objects.last().ftp_port, 9021)

        self.assertEqual(len(GalaxyInstanceTracking.objects.all()), git_before+1)

    def test_post_invalid_url(self):
        """
        Test to check init1 post (not sure how to get the post test working yet)
        """
        git_before = len(GalaxyInstanceTracking.objects.all())
        self.client.force_login(self.user)
        response = self.client.post('/galaxy/add_galaxy_instance/',
                                    {'url': 'www.notarealgalaxywebsite.com',
                                     'name':'test_local',
                                     'ftp_host':'http://127.0.0.1',
                                     'ftp_port':'9021'})

        self.assertEqual(response.status_code, 302)


class GalaxyUserCreateTestCase(TestCase):
    def setUp(self):
        setup_galaxy()
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_superuser(username='jacob', email='jacob@jacob.com',
                                                  password='top_secret'
                                                  )
        git = GalaxyInstanceTracking(url='http://127.0.0.1:9090',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=9021)
        git.save()
        self.git = git

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/add_galaxy_user/')

        request.user = AnonymousUser()
        request = add_message_and_session_middleware_to_request(request)

        response = GalaxyUserCreateView.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/galaxy/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('add_galaxy_user'))
        request.user = self.user
        response = GalaxyUserCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)  # done without error

    def test_post_valid_user(self):
        """
        """
        before = len(GalaxyUser.objects.all())
        self.client.force_login(self.user)
        response = self.client.post('/galaxy/add_galaxy_user/', {'email': 'john.doe@gmail.com',
                                                          'api_key': 'admin',
                                                                 'internal_user': self.user.id,
                                                           'galaxyinstancetracking': self.git.id})

        self.assertEqual(response.status_code, 302)  # redirected page (e.g. success page)
        self.assertEqual(GalaxyUser.objects.last().email, 'john.doe@gmail.com')
        self.assertEqual(GalaxyUser.objects.last().api_key, 'admin')
        self.assertEqual(GalaxyUser.objects.last().galaxyinstancetracking, self.git)
        self.assertEqual(len(GalaxyUser.objects.all()), before+1)

    def test_post_invalid_user(self):
        """
        """
        before = len(GalaxyUser.objects.all())
        self.client.force_login(self.user)
        response = self.client.post('/galaxy/add_galaxy_user/', {'email': 'john.doe@gmail.com',
                                                          'api_key': 'this is not an apikey',
                                                           'galaxyinstancetracking': self.git.id})

        self.assertEqual(response.status_code, 200)  # redirected page (e.g. success page)
        self.assertEqual(len(GalaxyUser.objects.all()), before)


class GalaxySyncCreateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_superuser(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:9090',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=9021)
        git.save()

        gu = GalaxyUser(email='john.doe@gmail.com',
                  api_key= 'admin',
                  galaxyinstancetracking = git,
                  internal_user=self.user)
        gu.save()

        self.git = git
        self.gu = gu

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/galaxy_sync/')

        request.user = AnonymousUser()
        request = add_message_and_session_middleware_to_request(request)

        response = GalaxySync.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/galaxy/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('galaxy_sync'))
        request.user = self.user
        response = GalaxySync.as_view()(request)
        self.assertEqual(response.status_code, 200)  # done without error


class WorkflowSummaryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_superuser(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:9090',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=9021)
        git.save()

        gu = GalaxyUser(email='john.doe@gmail.com',
                  api_key= 'admin',
                  galaxyinstancetracking = git,
                  internal_user=self.user)
        gu.save()

        self.git = git
        self.gu = gu

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/workflow_summary/')

        request.user = AnonymousUser()
        request = add_message_and_session_middleware_to_request(request)

        response = WorkflowListView.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/galaxy/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('workflow_summary'))
        request.user = self.user
        response = WorkflowListView.as_view()(request)
        self.assertEqual(response.status_code, 200)  # done without error


    def test_post_valid_sync(self):
        """
        """
        # Bioblend upload a workflow (todo)
        gi, gu = get_gi_gu(self.user, self.git)
        wc = WorkflowClient(gi)
        wc.import_workflow_from_local_path(os.path.join(os.path.dirname(__file__), 'data', 'simple-test-v1.ga'))

        beforeW = len(Workflow.objects.all())
        beforeWI = len(WorkflowInput.objects.all())

        self.client.force_login(self.user)
        response = self.client.post('/galaxy/workflow_summary/')

        print(Workflow.objects.all())
        afterW = len(Workflow.objects.all())
        afterWI = len(WorkflowInput.objects.all())

        self.assertEqual(response.status_code, 302)  # redirected page
        self.assertEqual(beforeW+1, afterW)
        self.assertLess(beforeWI, afterWI)

        self.assertEqual(Workflow.objects.last().added_by.username, 'jacob')
        self.assertEqual(Workflow.objects.last().name, 'simple-test')


class GenericFilesToGalaxyDataLibraryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_superuser(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:9090',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=9021)
        git.save()

        gu = GalaxyUser(email='john.doe@gmail.com',
                  api_key= '142d7a2ca37f2345c17dae69cfbd7155',
                  galaxyinstancetracking = git,
                  internal_user=self.user)
        gu.save()


        # data_zipfile_pth = os.path.join(os.path.dirname(__file__), 'data', 'mzml.zip')
        #
        # upload_files_from_zip(data_zipfile_pth, self.user)

        self.git = git
        self.gu = gu

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/galaxydatalib/')

        request.user = AnonymousUser()
        request = add_message_and_session_middleware_to_request(request)

        response = GenericFilesToGalaxyHistory.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/galaxy/')
#
#     # def test_get(self):
#     #     """
#     #     """
#     #     request = self.factory.get(reverse('galaxydatalib'))
#     #     request.user = self.user
#     #     response = GenericFilesToGalaxy.as_view()(request)
#     #     self.assertEqual(response.status_code, 200)  # done without error
#
#     #
#     # def test_post_valid_files(self):
#     #     """
#     #     """
#     #     this can't be check against a docker (without using some clever symlink setup) instead we only
#     #     check the history upload equivalent view
#
#
#
# class GenericFilesToGalaxyHistoryTestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
#         git = GalaxyInstanceTracking(url='http://127.0.0.1:9090',
#                                      name='test_local',
#                                      ftp_host='127.0.0.1',
#                                      ftp_port=9021)
#         git.save()
#
#         gu = GalaxyUser(email='john.doe@gmail.com',
#                   api_key= '142d7a2ca37f2345c17dae69cfbd7155',
#                   galaxyinstancetracking = git,
#                   user=self.user)
#         gu.save()
#
#
#         data_zipfile_pth = os.path.join(os.path.dirname(__file__), 'data', 'mzml.zip')
#
#         upload_files_from_zip(data_zipfile_pth, self.user)
#
#         self.git = git
#         self.gu = gu
#
#     def test_login_redirect(self):
#         """
#         Test to check if a guest user is redirect to the login page
#         """
#         request = self.factory.get('/galaxy/galaxyhistory/')
#
#         request.user = AnonymousUser()
#         request = add_middleware_to_request(request, SessionMiddleware)
#
#         response = GenericFilesToGalaxyHistory.as_view()(request)
#
#         # client acts as a fake website for the request
#         response.client = Client()
#
#         self.assertRedirects(response, '/login/?next=/galaxy/galaxyhistory/')
#
#     def test_get(self):
#         """
#         """
#         request = self.factory.get(reverse('galaxydatalib'))
#         request.user = self.user
#         response = GenericFilesToGalaxyHistory.as_view()(request)
#         self.assertEqual(response.status_code, 200)  # done without error
#
#     def test_post_valid_files(self):
#         """
#         """
#         before = len(GalaxyFileLink.objects.all())
#         self.client.force_login(self.user)
#
#         mids = [m.id for m in MFile.objects.all()]
#
#         data = {
#                  'galaxyinstancetracking': self.git.id,
#                  'check': mids,
#                  'history_name': 'test',
#                  'galaxy_password': 'password'
#                }
#
#         response = self.client.post('/galaxy/galaxyhistory/', data)
#
#         self.assertEqual(len(GalaxyFileLink.objects.all()), 4)
#
#
# #########################################################################################################
# # Will add some more test for running workflows, for mogi
# # class WorkflowRunTestCase(TestCase):
# #     def setUp(self):
# #         self.factory = RequestFactory()
# #         self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
# #         git = GalaxyInstanceTracking(url='http://127.0.0.1:8080',
# #                                      name='test_local',
# #                                      ftp_host='127.0.0.1',
# #                                      ftp_port=8021)
# #         git.save()
# #
# #         gu = GalaxyUser(email='john.doe@gmail.com',
# #                   api_key= '142d7a2ca37f2345c17dae69cfbd7155',
# #                   galaxyinstancetracking = git,
# #                   user=self.user)
# #         gu.save()
# #
# #
# #         data_zipfile_pth = os.path.join(os.path.dirname(__file__), 'data', 'mzml.zip')
# #
# #         upload_files_from_zip(data_zipfile_pth, self.user)
# #
# #         self.git = git
# #         self.gu = gu
# #
# #         workflow_sync(self.user)
# #
# #     def test_login_redirect(self):
# #         """
# #         Test to check if a guest user is redirect to the login page
# #         """
# #         request = self.factory.get('/galaxy/runworkflow/')
# #
# #         request.user = AnonymousUser()
# #         request = add_middleware_to_request(request, SessionMiddleware)
# #
# #         response = GenericFilesToGalaxyHistory.as_view()(request)
# #
# #         # client acts as a fake website for the request
# #         response.client = Client()
# #
# #         self.assertRedirects(response, '/dma/login/?next=/galaxy/runworkflow/')
# #
# #     def test_get(self):
# #         """
# #         """
# #         request = self.factory.get(reverse('runworkflow'))
# #         request.user = self.user
# #         response = WorkflowRun.as_view()(request)
# #         self.assertEqual(response.status_code, 200)  # done without error
# #
