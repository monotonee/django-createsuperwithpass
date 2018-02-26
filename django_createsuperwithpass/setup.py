"""
Note that include_package_data enables MANIFEST.in consumption.

See:
    https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
    https://docs.djangoproject.com/en/dev/intro/reusable-apps/#packaging-your-app

Using semantic versioning.

See:
    https://www.python.org/dev/peps/pep-0440/#public-version-identifiers
    http://semver.org/

"""

import pathlib
from setuptools import find_packages, setup


LONG_DESC = None
readme_path = pathlib.Path(__file__).resolve().with_name('README.rst')
if readme_path.is_file():
    LONG_DESC = readme_path.read_text(encoding='utf_8')


setup(
    name='django-createsuperwithpass',
    version='0.0.1',

    author='monotonee',
    author_email='monotonee@tuta.io',
    include_package_data=True, # Parses MANIFEST.in
    install_requires=[
        'django'
    ],
    extras_require={
        'dev': [
            'docker-compose',
            'mysqlclient',
            'pylint',
            'twine',
            'wheel'
        ]
    },
    license='MIT',
    packages=find_packages(exclude=('tests',)),
    # py_modules=['django_createsuperwithpass'],
    url='https://github.com/monotonee/django-createsuperwithpass',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    description=(
        'An override of Django\'s "createsuperuser" management command to allow non-interactive '
        'superuser password initialization.'
    ),
    keywords='createsuperuser deployment django management password user',
    long_description=LONG_DESC
)
