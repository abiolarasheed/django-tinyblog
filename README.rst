===================
django-tinyblog
===================

.. image:: https://travis-ci.org/abiolarasheed/django-tinyblog.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/abiolarasheed/django-tinyblog

.. image:: https://coveralls.io/repos/github/orangedigitallab/django-tinyblog/badge.svg
   :alt: Build Status
   :target: https://coveralls.io/github/abiolarasheed/django-tinyblog

Django Tiny Blog is a minimal configurable Django blogging app that allows you to focus on your blog content without the need of rolling out and maintaining your own.
You can customize the look and feel of the app without needing to modify the source code of the app, so that updates are painless and easy.

Features:

- Syntax highlighter
- Full-text Search.
- Pluggable configuration
- Simple admin interface.


Installation and usage
===================

Start by cloning ``django-tinyblog`` :

.. code:: bash

        git clone git@github.com:abiolarasheed/django-tinyblog.git


Create a virtual environment with a python >= 3.6 as a your interpreter and install pipenv.

.. code:: bash

    pip install --user pipenv
    pipenv install

Run your migrations

.. code:: bash

    python manage.py migrate



Customizing is as simple as creating a folder ``custom_dir`` on the same level as your ``django-tinyblog`` download:

.. code:: bash

    mkdir -p custom_dir/templates
    mkdir -p custom_dir/static/css
    mkdir -p custom_dir/static/js
    mkdir -p custom_dir/static/fonts
    touch  custom_dir/settings.py

Setting environment variable will help you control and customize your installation which you can set in your bashrc file or from the command line:

.. code:: bash

    export SECRET_KEY
    export BLOG_DATABASE_NAME
    export BLOG_DATABASE_USER
    export BLOG_DATABASE_PASSWORD
    export LANGUAGE_CODE
    export TIME_ZONE
    export HAS_INDEX_PAGE
    export INDEX_TEMPLATE
    export BROKER_URL
    export RESULT_BACKEND


After you've configured your environment variables, you can then runserver

.. code:: bash

    python manage.py runserver


Requirements
============

Django Tiny Blog's requirements are relatively easy.

* Python 3.6+
* Django 2.0+

Additionally, each backend has its own requirements. You should refer to the backend documentation for details.
