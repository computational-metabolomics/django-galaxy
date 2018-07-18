from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.libraries import LibraryClient

def test_galaxy_connection(url):


    # if not len(code_l) == 7:
    #     raise ValidationError()