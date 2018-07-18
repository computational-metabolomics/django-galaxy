=====
django-galaxy
=====


|Build Status (Travis)| |Py versions|


Django interfacing with Galaxy. Backend using the bioblend API.

`Galaxy <https://galaxyproject.org/>`__ is a web based workflow platform that can be used to perform bioinformatics in a reproducible and sharable environment.

Further documentation available on `ReadTheDocs <https://mogi.readthedocs.io/en/latest/>`__

Quick start
-----------

1. Add "galaxy" to your INSTALLED_APPS setting like this (note that this app depends on gfiles)::

    INSTALLED_APPS = [
        ...
        'gfiles',
        'galaxy'

        'django_tables2',
        'django_tables2_column_shifter',
        'django_filters',
        'bootstrap3',
        'django_sb_admin',

    ]

2. Include the polls URLconf in your project urls.py like this::

    path('galaxy/', include('galaxy.urls')),

3. Run `python manage.py migrate` to create the polls models.


.. |Build Status (Travis)| image:: https://travis-ci.com/computational-metabolomics/django-galaxy.svg?branch=master
   :target: https://travis-ci.com/computational-metabolomics/django-galaxy/

.. |Py versions| image:: https://img.shields.io/pypi/pyversions/django-galaxy.svg?style=flat&maxAge=3600
   :target: https://pypi.python.org/pypi/django-galaxy/