from setuptools import setup, find_packages
import os

version = __import__('live_support').__version__

install_requires = [
    'setuptools',
    'simplejson',
    'django>=1.3',
]

setup(
    name = "django-live-support",
    version = version,
    url = 'http://github.com/megamark16/django-live-support',
    license = 'BSD',
    platforms=['OS Independent'],
    description = "A django app that lets you chat with visitors to your site.",
    author = "Mark Ransom",
    author_email = 'megamark16@gmail.com',
    packages=find_packages(),
    install_requires = install_requires,
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Communications :: Chat',
    ],
    package_dir={
        'live_support': 'live_support',
    },
)
