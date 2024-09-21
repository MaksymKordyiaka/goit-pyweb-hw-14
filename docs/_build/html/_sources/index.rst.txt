.. rest app documentation master file, created by
   sphinx-quickstart on Mon Sep 16 16:15:48 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

rest app documentation
======================

This is the documentation for the REST API built with FastAPI. The API allows users to manage contacts, perform CRUD operations, search for contacts, and retrieve contacts with upcoming birthdays.

Features of the REST API include:
- User authentication with JWT tokens
- Contact management (CRUD operations)
- Searching for contacts by name or email
- Retrieving contacts with upcoming birthdays


.. toctree::
   :maxdepth: 2
   :caption: Contents:

REST APP main
=============

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:

REST APP repository contacts
============================

.. automodule:: repository.contacts
  :members:
  :undoc-members:
  :show-inheritance:

REST APP repository users
============================

.. automodule:: repository.users
  :members:
  :undoc-members:
  :show-inheritance:

REST APP routes auth
============================

.. automodule:: routes.auth
  :members:
  :undoc-members:
  :show-inheritance:

REST APP routes contacts
============================

.. automodule:: routes.contacts
  :members:
  :undoc-members:
  :show-inheritance:

REST APP routes users
============================

.. automodule:: routes.users
  :members:
  :undoc-members:
  :show-inheritance:

REST APP services auth
=========================
.. automodule:: services.auth
  :members:
  :undoc-members:
  :show-inheritance:

REST APP services email
=========================
.. automodule:: services.email
  :members:
  :undoc-members:
  :show-inheritance:


REST APP services rate limiter
=========================
.. automodule:: services.rate_limiter
  :members:
  :undoc-members:
  :show-inheritance: