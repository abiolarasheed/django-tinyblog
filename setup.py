# -*- coding: utf-8 -*-
from distutils.core import setup
import tinyblog

required = []
with open('requirements.txt') as f:
    required.extend(f.read().splitlines())


setup(
    name='django-tinyblog',
    version=tinyblog.__version__,
    packages=['blog', 'blog.tests', 'blog.migrations', 'tinyblog'],
    url='https://github.com/orangedigitallab/django-tinyblog.git',
    license='MIT License',
    author='Abiola Rasheed',
    author_email='rasheed.abiola3@gmail.com',
    description='A mini django blogging app written in python3.6+ ',
    long_description=open('README.rst').read(),
    keywords=['forms', 'django', 'crispy', 'DRY'],
    install_requires=required,
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
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
