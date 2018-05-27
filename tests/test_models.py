# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from galaxy.models import GalaxyInstance, GalaxyUser
from dma.utils import save_model_list
from django.core.exceptions import ValidationError

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






# class CreateISAModelTestCase(TestCase):
#     def setUp(self):
#         sample_class_input = ['ANIMAL', 'BLANK', 'COMPOUND']
#         self.sampletypes = [SampleType.objects.create(type=i) for i in sample_class_input]
#
#         m_input = ['DI-MS', 'DI-MSn', 'LC-MS', 'LC-MSMS']
#         self.measurement_techniques = [MeasurementTechnique.objects.create(type=i) for i in m_input]
#
#         p_input = ['POS', 'NEG', 'NA']
#         self.polarities = [PolarityType.objects.create(type=i) for i in p_input]
#
#         self.org = Organism.objects.create(name='Daphnia magna')
#         self.org.save()
#
#         extraction_input = ['AP', 'P']
#         self.extractions = [ExtractionType.objects.create(type=e) for e in extraction_input]
#
#         spe_input = ['WAX', 'WCX', 'C18']
#         self.spes = [SpeType.objects.create(type=e) for e in spe_input]
#
#         lc_input = ['C30', 'C18']
#         self.chrom = [ChromatographyType.objects.create(type=e) for e in lc_input]
#
#         self.investigation = Investigation()
#         self.investigation.save()
#         self.study = Study(investigation=self.investigation, dmastudy=True)
#         self.study.save()
#
#         save_model_list(self.extractions)
#         save_model_list(self.spes)
#         save_model_list(self.chrom)
#         save_model_list(self.measurement_techniques)
#         save_model_list(self.sampletypes)
#
#
#     def create_lcms_lcmsms_assay(self):
#         sample1 = StudySample(study=self.study, sample_name='Daphnia pooled sample', sampletype=self.sampletypes[0])
#         sample2 = StudySample(study=self.study, sample_name='blank extract', sampletype=self.sampletypes[1])
#         sample3 = StudySample(study=self.study, sample_name='Reference compound', sampletype=self.sampletypes[2])
#
#         sample1.save()
#         sample2.save()
#         sample3.save()
#
#         assay = Assay(study=self.study, description='AP_WAX[1]_C30[0]_LC-MS_LC_MSMS')
#         assay.save()
#
#         # ANIMAL_WAX[1]_C30[0]_LC-MS_POS
#         assay_detail1 = AssayDetail(assay=assay,
#                     studysample=sample1,
#                     extractiontype=self.extractions[0],
#                     spetype=self.spes[0],
#                     spefrac=1,
#                     chromatographytype=self.chrom[0],
#                     chromatographyfrac = 0,
#                     measurementtechnique= self.measurement_techniques[2],
#                     polaritytype= self.polarities[0])
#         assay_detail1.save()
#
#         # ANIMAL_WAX[1]_C30[0]_LC-MSMS_POS
#         assay_detail2 = AssayDetail(assay=assay,
#                                     studysample=sample1,
#                                     extractiontype=self.extractions[0],
#                                     spetype=self.spes[0],
#                                     spefrac=1,
#                                     chromatographytype=self.chrom[0],
#                                     chromatographyfrac=0,
#                                     measurementtechnique=self.measurement_techniques[3],
#                                     polaritytype=self.polarities[0])
#         assay_detail2.save()
#
#         # ANIMAL_WAX[1]_C30[0]_LC-MSMS_NEG
#         assay_detail3 = AssayDetail(assay=assay,
#                                     studysample=sample1,
#                                     extractiontype=self.extractions[0],
#                                     spetype=self.spes[0],
#                                     spefrac=1,
#                                     chromatographytype=self.chrom[0],
#                                     chromatographyfrac=0,
#                                     measurementtechnique=self.measurement_techniques[3],
#                                     polaritytype=self.polarities[1])
#         assay_detail3.save()
#
#         self.assertEqual(assay_detail1.code_field, 'ANIMAL_AP_WAX[1]_C30[0]_LC-MS_POS')
#
#
#

# class WorkflowStageModelTestCase(TestCase):
#     def setUp(self):
#         sample_class_input = ['A', 'B', 'C']
#         self.sampleclasses = [SampleClass.objects.create(sample_class=i) for i in sample_class_input]
#
#         m_input = ['DI-MS', 'DI-MSn', 'LC-MS', 'LC-MSMS']
#         self.measurement_techniques = [MeasurementTechnique.objects.create(type=i) for i in m_input]
#
#         p_input = ['POS', 'NEG', 'NA']
#         self.polarities = [PolarityType.objects.create(type=i) for i in p_input]
#
#         self.org = Organism.objects.create(name='Daphnia magna')
#         self.org.save()
#
#         extraction_input = ['AP', 'P']
#         self.extractions = [ExtractionType.objects.create(type=e) for e in extraction_input]
#
#         spe_input = ['WAX', 'WCX', 'C18']
#         self.spes = [SpeType.objects.create(type=e) for e in spe_input]
#
#         lc_input = ['C30', 'C18']
#         self.lcs = [LcType.objects.create(type=e) for e in lc_input]
#
#         save_model_list(self.extractions)
#         save_model_list(self.spes)
#         save_model_list(self.lcs)
#         save_model_list(self.measurement_techniques)
#         save_model_list(self.sampleclasses)
#
#     def test_code_field_auto(self):
#         """
#         check codefield is created automatically
#         """
#
#         ws = WorkflowStage(sampleclass=self.sampleclasses[0],
#                              extractiontype=self.extractions[0],
#                              spetype=self.spes[0],
#                              spefrac=1,
#                              lctype=self.lcs[0],
#                              lcfrac=1,
#                              measurementtechnique=self.measurement_techniques[0],
#                              polaritytype=self.polarities[0])
#         ws.save()
#
#         self.assertEqual(ws.code_field, 'A_AP_WAX[1]_C30[1]_DI-MS_POS')
#
#     def test_duplicate_check(self):
#         """
#         Test for duplicates
#         """
#
#         ws = WorkflowStage(sampleclass=self.sampleclasses[0],
#                              extractiontype=self.extractions[0],
#                              spetype=self.spes[0],
#                              spefrac=1,
#                              lctype=self.lcs[0],
#                              lcfrac=1,
#                              measurementtechnique=self.measurement_techniques[0],
#                              polaritytype=self.polarities[0])
#         ws.save()
#
#
#         with self.assertRaises(Exception) as raised:  # top level exception as we want to figure out its exact type
#             ws = WorkflowStage(sampleclass=self.sampleclasses[0],
#                                extractiontype=self.extractions[0],
#                                spetype=self.spes[0],
#                                spefrac=1,
#                                lctype=self.lcs[0],
#                                lcfrac=1,
#                                measurementtechnique=self.measurement_techniques[0],
#                                polaritytype=self.polarities[0])
#             ws.save()
#
#         self.assertEqual(IntegrityError, type(raised.exception))
#











