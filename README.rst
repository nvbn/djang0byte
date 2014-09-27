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

- Deploy all required components::

    $ python deploy.py

Here it is!


RPC API
=======
Interface -- ``/json/``

Objects
-------
**Post**
 - ``author`` -- ``User``
 - ``title`` -- ``unicode``
 - ``date`` -- ``datetime``
 - ``blog`` -- ``Blog``
 - ``rate`` -- ``int``
 - ``rate_count`` -- ``int``

**Draft**
 - ``author`` -- ``User``
 - ``title`` -- ``unicode``
 - ``blog`` -- ``Blog``

**Blog**
 - ``name`` -- ``unicode``
 - ``description`` -- ``unicode``
 - ``rate`` -- ``int``
 - ``rate_count`` -- ``int``

**Comment**
 - ``post`` -- ``Post``
 - ``text`` -- ``unicode``
 - ``rate`` -- ``int``
 - ``rate_count`` -- ``int``
 - ``created`` -- ``datetime``

Methods
-------
 - ``main.rate_post(id=int, value=bool) -> {error=str}`` -- Rate post
 - ``main.rate_comment(id=int, value=bool) -> {error=str}`` -- Rate comment
 - ``main.rate_blog(id=int, value=bool) -> {error=str}`` -- Rate blog
 - ``main.preview_comment(text=unicode) -> {text=unicode}`` -- Get comment preview
 - ``main.change_favourite(post_id=int) -> Post`` -- change favourite
 - ``main.change_spy(post_id=int) -> Post`` -- change spy
 - ``main.get_last_comments(count=int, panel=bool) -> [Comment]`` -- Get last comments
 - ``main.get_last_posts(count=int, panel=bool) -> [Post]`` -- Get last posts
 - ``main.get_users(count=int, panel=bool) -> [User]`` -- Get users
 - ``main.get_blogs(count=int, panel=bool) -> [Blog]`` -- Get blogs
 - ``main.get_favourites(count=int, panel=bool) -> [Post]`` -- Get favourites
 - ``main.get_spies(count=int, panel=bool) -> [Post]`` -- Get spied posts
 - ``main.get_drafts(count=int, panel=bool) -> [Draft]`` -- Get drafts
 - ``main.join_blog(blog_id=int) -> {status=bool}`` -- Join or withdraw blog
 - ``main.post_options(post_id=int, disable_rate=bool, disable_reply=bool, pinch=bool) -> Post`` -- Change post options
