#!/usr/bin/env python3
from setuptools import setup


setup(
  name = 'cikumeta',
  packages = [
      'cikuservice',
      'cikuservice.types',
      'cikuservice.auth',
      'cikuservice.blueprints',
      'cikuservice.blueprints.api',
  ],
  version = '1.0',
  description = 'kicikku account service template',
  author = 'Firas Rafislam',
  author_email = 'firas@kicikku.com',
  url = 'https://github.com/literasibadguy/cikumeta',
  install_requires = [
      'alembic',
      'bcrypt',
      'dnspython',
      'qrcode',
      'redis',
      'stripe',
      'prometheus_client',
      'zxcvbn'
  ],
  extras_require = {
      'unix-pam-auth': ['python_pam'],
  },
  license = '',
  package_data={
      'cikuservice': [
          'templates/*.html',
          'static/*',
          'static/icons/*',
          'emails/*',
          'schema.graphqls',
          'default_query.graphql',
      ]
  },
  scripts = [
  ]
)

