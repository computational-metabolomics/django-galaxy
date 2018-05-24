=====
misa
=====

ISA organisation for metabolomic studies with Django

Detailed documentation is in the "docs" directory (todo)

Quick start
-----------

1. Add "galaxy" to your INSTALLED_APPS setting like this (note that this app depends on gfiles)::

    INSTALLED_APPS = [
        ...
        'gfiles',
        'galaxy'
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('galaxy/', include('galaxy.urls')),

3. Run `python manage.py migrate` to create the polls models.
