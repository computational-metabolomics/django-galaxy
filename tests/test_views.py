# -*- coding: utf-8 -*-
#  python manage.py test misa -v 3 --keepdb
#  coverage run --source='.' manage.py test galaxy -v 3 --keepdb
#  coverage report
#  coverage html --omit="admin.py"
from __future__ import unicode_literals

import os

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory, Client
from django.core.urlresolvers import reverse

from galaxy.views import GalaxyInstanceCreateView, GalaxyUserCreateView, WorkflowSync,\
    WorkflowListView, GenericFilesToGalaxy, GenericFilesToGalaxyHistory
from galaxy.models import GalaxyInstanceTracking, GalaxyUser, Workflow, WorkflowInput, GalaxyFileLink

from metab.models.models import MFile
from metab.utils.mfile_upload import upload_files_from_zip

def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def add_middleware_to_response(request, middleware_class):
    middleware = middleware_class()
    middleware.process_response(request)
    return request

class GalaxyInstanceCreateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/addgi/')

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)
        response = GalaxyInstanceCreateView.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/dma/login/?next=/galaxy/addgi/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('addgi'))
        request.user = self.user
        response = GalaxyInstanceCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200) # done without error


    def test_post_valid_url(self):
        """
        Test post with valid url
        """
        git_before = len(GalaxyInstanceTracking.objects.all())

        self.client.force_login(self.user)
        response = self.client.post('/galaxy/addgi/',
                                    {'url': 'http://127.0.0.1:8080',
                                     'name':'test_local',
                                     'ftp_host':'http://127.0.0.1',
                                     'ftp_port':'8021'})

        self.assertEqual(response.status_code, 302) # redirected page (e.g. success page)
        self.assertEqual(GalaxyInstanceTracking.objects.last().url,  'http://127.0.0.1:8080')
        self.assertEqual(GalaxyInstanceTracking.objects.last().name, 'test_local')
        self.assertEqual(GalaxyInstanceTracking.objects.last().ftp_host, 'http://127.0.0.1')
        self.assertEqual(GalaxyInstanceTracking.objects.last().ftp_port, 8021)

        self.assertEqual(len(GalaxyInstanceTracking.objects.all()), git_before+1)


    def test_post_invalid_url(self):
        """
        Test to check init1 post (not sure how to get the post test working yet)
        """
        git_before = len(GalaxyInstanceTracking.objects.all())
        self.client.force_login(self.user)
        response = self.client.post('/galaxy/addgi/',
                                    {'url': 'www.notarealgalaxywebsite.com',
                                     'name':'test_local',
                                     'ftp_host':'http://127.0.0.1',
                                     'ftp_port':'8021'})


        self.assertEqual(response.status_code, 200) # should just show the original page
        self.assertEqual(len(GalaxyInstanceTracking.objects.all()), git_before)


class GalaxyUserCreateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:8080',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=8021)
        git.save()
        self.git = git

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/addguser/')

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)

        response = GalaxyUserCreateView.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        print 'LOGIN REDIRECT', response
        self.assertRedirects(response, '/dma/login/?next=/galaxy/addguser/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('addguser'))
        request.user = self.user
        response = GalaxyUserCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)  # done without error

    def test_post_valid_user(self):
        """
        """
        before = len(GalaxyUser.objects.all())
        self.client.force_login(self.user)
        response = self.client.post('/galaxy/addguser/', {'email': 'john.doe@gmail.com',
                                                          'api_key': '142d7a2ca37f2345c17dae69cfbd7155',
                                                           'galaxyinstancetracking': self.git.id})

        self.assertEqual(response.status_code, 302)  # redirected page (e.g. success page)
        self.assertEqual(GalaxyUser.objects.last().email, 'john.doe@gmail.com')
        self.assertEqual(GalaxyUser.objects.last().api_key, '142d7a2ca37f2345c17dae69cfbd7155')
        self.assertEqual(GalaxyUser.objects.last().galaxyinstancetracking, self.git)
        self.assertEqual(len(GalaxyUser.objects.all()), before+1)


    def test_post_invalid_user(self):
        """
        """
        before = len(GalaxyUser.objects.all())
        self.client.force_login(self.user)
        response = self.client.post('/galaxy/addguser/', {'email': 'john.doe@gmail.com',
                                                          'api_key': 'this is not an apikey',
                                                           'galaxyinstancetracking': self.git.id})

        self.assertEqual(response.status_code, 200)  # redirected page (e.g. success page)
        self.assertEqual(len(GalaxyUser.objects.all()), before)


class GalaxySyncCreateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:8080',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=8021)
        git.save()

        gu = GalaxyUser(email='john.doe@gmail.com',
                  api_key= '142d7a2ca37f2345c17dae69cfbd7155',
                  galaxyinstancetracking = git,
                  user=self.user)
        gu.save()

        self.git = git
        self.gu = gu

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/workflow_sync/')

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)

        response = WorkflowSync.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/dma/login/?next=/galaxy/workflow_sync/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('workflow_sync'))
        request.user = self.user
        response = WorkflowSync.as_view()(request)
        self.assertEqual(response.status_code, 200)  # done without error

    def test_post(self):
        """
        """
        beforeW = len(Workflow.objects.all())
        beforeWI = len(WorkflowInput.objects.all())

        self.client.force_login(self.user)
        response = self.client.post('/galaxy/workflow_sync/')

        afterW = len(Workflow.objects.all())
        afterWI = len(WorkflowInput.objects.all())

        self.assertEqual(response.status_code, 302)  # redirected page
        self.assertEqual(beforeW+1, afterW)
        self.assertLess(beforeWI, afterWI)

        self.assertEqual(Workflow.objects.last().added_by.username, 'jacob')
        self.assertEqual(Workflow.objects.last().name, 'simple-xcms')




class WorkflowSummaryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:8080',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=8021)
        git.save()

        gu = GalaxyUser(email='john.doe@gmail.com',
                  api_key= '142d7a2ca37f2345c17dae69cfbd7155',
                  galaxyinstancetracking = git,
                  user=self.user)
        gu.save()

        self.git = git
        self.gu = gu

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/workflow_summary/')

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)

        response = WorkflowListView.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/dma/login/?next=/galaxy/workflow_summary/')

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
        beforeW = len(Workflow.objects.all())
        beforeWI = len(WorkflowInput.objects.all())

        self.client.force_login(self.user)
        response = self.client.post('/galaxy/workflow_summary/')

        afterW = len(Workflow.objects.all())
        afterWI = len(WorkflowInput.objects.all())

        self.assertEqual(response.status_code, 302)  # redirected page
        self.assertEqual(beforeW+1, afterW)
        self.assertLess(beforeWI, afterWI)

        self.assertEqual(Workflow.objects.last().added_by.username, 'jacob')
        self.assertEqual(Workflow.objects.last().name, 'simple-xcms')


class GenericFilesToGalaxyDataLibraryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:8080',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=8021)
        git.save()

        gu = GalaxyUser(email='john.doe@gmail.com',
                  api_key= '142d7a2ca37f2345c17dae69cfbd7155',
                  galaxyinstancetracking = git,
                  user=self.user)
        gu.save()


        data_zipfile_pth = os.path.join(os.path.dirname(__file__), 'data', 'mzml.zip')

        upload_files_from_zip(data_zipfile_pth, self.user)

        self.git = git
        self.gu = gu

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/galaxydatalib/')

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)

        response = GenericFilesToGalaxy.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/dma/login/?next=/galaxy/galaxydatalib/')

    # def test_get(self):
    #     """
    #     """
    #     request = self.factory.get(reverse('galaxydatalib'))
    #     request.user = self.user
    #     response = GenericFilesToGalaxy.as_view()(request)
    #     self.assertEqual(response.status_code, 200)  # done without error

    #
    # def test_post_valid_files(self):
    #     """
    #     """
    #     this can't be check against a docker (without using some clever symlink setup) instead we only
    #     check the history upload equivalent view



class GenericFilesToGalaxyHistoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
        git = GalaxyInstanceTracking(url='http://127.0.0.1:8080',
                                     name='test_local',
                                     ftp_host='127.0.0.1',
                                     ftp_port=8021)
        git.save()

        gu = GalaxyUser(email='john.doe@gmail.com',
                  api_key= '142d7a2ca37f2345c17dae69cfbd7155',
                  galaxyinstancetracking = git,
                  user=self.user)
        gu.save()


        data_zipfile_pth = os.path.join(os.path.dirname(__file__), 'data', 'mzml.zip')

        upload_files_from_zip(data_zipfile_pth, self.user)

        self.git = git
        self.gu = gu

    def test_login_redirect(self):
        """
        Test to check if a guest user is redirect to the login page
        """
        request = self.factory.get('/galaxy/galaxyhistory/')

        request.user = AnonymousUser()
        request = add_middleware_to_request(request, SessionMiddleware)

        response = GenericFilesToGalaxyHistory.as_view()(request)

        # client acts as a fake website for the request
        response.client = Client()

        self.assertRedirects(response, '/dma/login/?next=/galaxy/galaxyhistory/')

    def test_get(self):
        """
        """
        request = self.factory.get(reverse('galaxydatalib'))
        request.user = self.user
        response = GenericFilesToGalaxy.as_view()(request)
        self.assertEqual(response.status_code, 200)  # done without error

    def test_post_valid_files(self):
        """
        """
        before = len(GalaxyFileLink.objects.all())
        self.client.force_login(self.user)

        mids = [m.id for m in MFile.objects.all()]

        data = {
                 'galaxyinstancetracking': self.git.id,
                 'check': mids,
                 'history_name': 'test',
                 'galaxy_password': 'password'
               }

        response = self.client.post('/galaxy/galaxyhistory/', data)

        self.assertEqual(len(GalaxyFileLink.objects.all()), 4)


#########################################################################################################
# Will add some more test for running workflows, for mogi
# class WorkflowRunTestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')
#         git = GalaxyInstanceTracking(url='http://127.0.0.1:8080',
#                                      name='test_local',
#                                      ftp_host='127.0.0.1',
#                                      ftp_port=8021)
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
#         workflow_sync(self.user)
#
#     def test_login_redirect(self):
#         """
#         Test to check if a guest user is redirect to the login page
#         """
#         request = self.factory.get('/galaxy/runworkflow/')
#
#         request.user = AnonymousUser()
#         request = add_middleware_to_request(request, SessionMiddleware)
#
#         response = GenericFilesToGalaxyHistory.as_view()(request)
#
#         # client acts as a fake website for the request
#         response.client = Client()
#
#         self.assertRedirects(response, '/dma/login/?next=/galaxy/runworkflow/')
#
#     def test_get(self):
#         """
#         """
#         request = self.factory.get(reverse('runworkflow'))
#         request.user = self.user
#         response = WorkflowRun.as_view()(request)
#         self.assertEqual(response.status_code, 200)  # done without error
#
