=====
django-galaxy
=====


Django interfacing with Galaxy. Backend using the bioblend API.

`Galaxy <https://galaxyproject.org/>`__ is a web based workflow platform that can be used to perform bioinformatics in a reproducible and sharable environment.

Used to create `DMAdb <https://mogi.readthedocs.io/en/latest/>`__, see `ReadTheDocs (DMAdb) <https://dmadb.readthedocs.io/en/latest/getting-started.html>`__ for documentation.

Previous documentation can be found at `ReadTheDocs (legacy) <https://mogi.readthedocs.io/en/latest/>`__.

PyPI Archive Notice
-------------------

This package is no longer updated on PyPI.

For current code and updates, use this `GitHub repository <https://github.com/computational-metabolomics/django-galaxy>`__.


Quick start
-----------

1. Add "galaxy" and django application dependencies to your INSTALLED_APPS setting like this (galaxy should come before gfiles)::

    INSTALLED_APPS = [
        ...
        'galaxy',
        'gfiles',


        'django_tables2',
        'bootstrap3',
        'django_tables2_column_shifter',
        'django_sb_admin',
        'django_filter'
    ]

2. Include the polls URLconf in your project urls.py like this::

    url(r'^', include('gfiles.urls')),
    url('galaxy/', include('galaxy.urls')),

3. Run `python manage.py migrate` to create the models.

4. Start the development server and visit http://127.0.0.1:8000

