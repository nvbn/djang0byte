Djang0byte
==========

Lightweight social networks engine written in python+django, that aims to bear great workloads.
Features:

- Tree comments with rating;
- Blogs that contain posts, have their own rating, which in turn affects owner's rating;
- Posts (articles) with rating and tags;
- Notify system with last action feed;
- Private messages;
- Full text search;
- Code highlighting.

Install
=======

For install copy settings/dist.py to settings/local.py, set db settings and run deploy.py.

Using VirtualEnv
----------------

To use ``virtualenv`` with Djang0byte you can do the following:

- Create a virtual environment, e.g.::
    
    $ virtualenv /var/tmp/djang0byte-env

- Configure database in ``settings/local.py`` as stated above, e.g.::

    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = '/var/tmp/djang0byte.sqlite3'

- Make sure that ``xapian`` module is available in the virtual environment
  (it is not available on PyPI), e.g.::

    $ ln -s /usr/lib/python2.7/dist-packages/xapian/ /var/tmp/djang0byte-env/lib/python2.7/site-packages/

- Switch to the virtual environment::

    $ . /var/tmp/djang0byte-env/bin/activate

- Install all required components::

    $ pip install -r requirements

Here it is!

