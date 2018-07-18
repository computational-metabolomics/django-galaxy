# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
# from django.test import TestCase
# from django.contrib.auth.models import AnonymousUser, User
# from galaxy.models import GalaxyInstanceTracking, GalaxyUser
#
# class GalaxyUserModelTestCase(TestCase):
#
#     def test_instance_create_invalid_url(self):
#         """
#         Test creation of Galaxy instance model
#         """
#         user = User.objects.create_user(
#             username='jacob2', email='jacob@…', password='top_secret')
#
#         gi = GalaxyInstance(url='https://public.phenomenal-h2020.eu/', name='phenomenal')
#         gi.save()
#
#         gu = GalaxyUser(user=user, hashed_api_key='d8f5a201a90d7354174decc3e454a842', galaxyinstance=gi)