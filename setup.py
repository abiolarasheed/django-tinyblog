# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.core import setup

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

import tinyblog


project_file = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(project_file["packages"], r=False)


setup(
    name="django-tinyblog",
    version=tinyblog.__version__,
    packages=["blog", "blog.tests", "blog.migrations", "tinyblog"],
    url="https://github.com/orangedigitallab/django-tinyblog.git",
    license="MIT License",
    author="Abiola Rasheed",
    author_email="rasheed.abiola3@gmail.com",
    description="A mini django blogging app written in python3.6+.",
    long_description=open("README.rst").read(),
    keywords=["blog", "django", "tinyblog", "tiny"],
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
