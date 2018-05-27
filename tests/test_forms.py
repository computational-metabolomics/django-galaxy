# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
#
# from django.test import TestCase
# from isa.forms import AssayDetail
# from dma.utils import save_model_list
#
# from isa.models import ChromatographyType, SpeType, ExtractionType, MeasurementTechnique, Organism, SampleType, PolarityType
# from isa.models import Investigation, Study, StudySample, Assay, AssayDetail
# from isa.forms import AssayDetailForm, UploadAssayDataFilesForm
# import os
#
# from django.core.files.uploadedfile import SimpleUploadedFile
#
# class AssayDetailFormTestCase(TestCase):
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
#     def test_form_submission(self):
#         """
#         Test to check unit testing running
#         """
#         #Using a model form as a validator that is not a HTTP request (as per page 165 of Two Scoops of Django 1.11
#         sample1 = StudySample(study=self.study, sample_name='Daphnia pooled sample', sampletype=self.sampletypes[0])
#
#         sample1.save()
#
#         assay = Assay(study=self.study, description='AP_WAX[1]_C30[0]_LC-MS_LC_MSMS')
#         assay.save()
#
#         data_in = { 'assay':assay.id,
#                     'studysample':sample1.id,
#                     'extractiontype':self.extractions[0].id,
#                     'spetype':self.spes[0].id,
#                     'spefrac':1,
#                     'chromatographytype':self.chrom[0].id,
#                     'chromatographyfrac':0,
#                     'measurementtechnique':self.measurement_techniques[2].id,
#                     'polaritytype':self.polarities[0].id}
#
#         form = AssayDetailForm(data_in)
#         print form.errors
#
#         self.assertTrue(form.is_valid())
#
#         print form.errors
#         ad = form.save()
#
#         self.assertEqual(ad.chromatographyfrac, 0)
#         self.assertEqual(ad.spefrac, 1)
#         self.assertEqual(ad.code_field, 'ANIMAL_AP_WAX[1]_C30[0]_LC-MS_POS')
#         self.assertIs(len(AssayDetail.objects.all()), 1)
#
#
# class UploadAssayDataFilesFormTestCase(TestCase):
#     def setUp(self):
#         upload_assay_data_form_setup(self)
#
#     def test_upload_assay_data_files(self):
#         """
#         Test to check unit testing running
#         """
#         # Using a model form as a validator that is not a HTTP request (as per page 165 of Two Scoops of Django 1.11
#         data_zipfile_pth = os.path.join(os.path.dirname(__file__), 'data', 'DUMMY_P_WAX1_PHE.zip')
#         data_zipfile = SimpleUploadedFile('DUMMY_P_WAX1_PHE.zip', open(data_zipfile_pth, 'r').read())
#
#         form = UploadAssayDataFilesForm('{}', {'data_zipfile': data_zipfile})
#
#         # self.assertTrue(form.is_valid())
#         self.assertTrue(form.is_valid())
#
#         print form
#         print form.errors
#         print form.cleaned_data
#         print form.cleaned_data['data_zipfile']
#
#
#
# def upload_assay_data_form_setup(self):
#     sample_class_input = ['ANIMAL', 'BLANK', 'COMPOUND']
#     self.sampletypes = [SampleType.objects.create(type=i) for i in sample_class_input]
#
#     m_input = ['DI-MS', 'DI-MSn', 'LC-MS', 'LC-MSMS']
#     self.measurement_techniques = [MeasurementTechnique.objects.create(type=i) for i in m_input]
#
#     p_input = ['POS', 'NEG', 'NA']
#     self.polarities = [PolarityType.objects.create(type=i) for i in p_input]
#
#     self.org = Organism.objects.create(name='Daphnia magna')
#     self.org.save()
#
#     extraction_input = ['AP', 'P']
#     self.extractions = [ExtractionType.objects.create(type=e) for e in extraction_input]
#
#     spe_input = ['WAX', 'WCX', 'C18']
#     self.spes = [SpeType.objects.create(type=e) for e in spe_input]
#
#     lc_input = ['C30', 'C18']
#     self.chrom = [ChromatographyType.objects.create(type=e) for e in lc_input]
#
#     self.investigation = Investigation()
#     self.investigation.save()
#     self.study = Study(investigation=self.investigation, dmastudy=True)
#     self.study.save()
#
#     save_model_list(self.extractions)
#     save_model_list(self.spes)
#     save_model_list(self.chrom)
#     save_model_list(self.measurement_techniques)
#     save_model_list(self.sampletypes)
#
#     sample1 = StudySample(study=self.study, sample_name='Daphnia pooled sample', sampletype=self.sampletypes[0])
#     sample1.save()
#
#     sample2 = StudySample(study=self.study, sample_name='blank sample', sampletype=self.sampletypes[1])
#     sample2.save()
#
#     assay = Assay(study=self.study, description='AP_WAX[1]_C30[0]_LC-MS')
#     assay.save()
#
#     data_in1 = {'assay': assay.id,
#                 'studysample': sample1.id,
#                 'extractiontype': self.extractions[0].id,
#                 'spetype': self.spes[0].id,
#                 'spefrac': 1,
#                 'chromatographytype': self.chrom[0].id,
#                 'chromatographyfrac': 0,
#                 'measurementtechnique': self.measurement_techniques[2].id,
#                 'polaritytype': self.polarities[0].id}
#
#     data_in2 = {'assay': assay.id,
#                 'studysample': sample2.id,
#                 'extractiontype': self.extractions[0].id,
#                 'spetype': self.spes[0].id,
#                 'spefrac': 1,
#                 'chromatographytype': self.chrom[0].id,
#                 'chromatographyfrac': 0,
#                 'measurementtechnique': self.measurement_techniques[2].id,
#                 'polaritytype': self.polarities[0].id}
#
#     data_in3 = {'assay': assay.id,
#                 'studysample': sample1.id,
#                 'extractiontype': self.extractions[0].id,
#                 'spetype': self.spes[0].id,
#                 'spefrac': 1,
#                 'chromatographytype': self.chrom[0].id,
#                 'chromatographyfrac': 0,
#                 'measurementtechnique': self.measurement_techniques[2].id,
#                 'polaritytype': self.polarities[1].id}
#
#     data_in4 = {'assay': assay.id,
#                 'studysample': sample2.id,
#                 'extractiontype': self.extractions[0].id,
#                 'spetype': self.spes[0].id,
#                 'spefrac': 1,
#                 'chromatographytype': self.chrom[0].id,
#                 'chromatographyfrac': 0,
#                 'measurementtechnique': self.measurement_techniques[2].id,
#                 'polaritytype': self.polarities[1].id}
#
#     for data_in in [data_in1, data_in2, data_in3, data_in4]:
#         form = AssayDetailForm(data_in)
#         form.is_valid()
#         ad = form.save()
#
