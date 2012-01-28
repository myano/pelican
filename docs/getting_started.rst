Getting started
###############

Installing
==========

You're ready? Let's go ! You can install pelican in a lot of different ways,
the simpler one is via `pip <http://pip.openplans.org/>`_::

    $ pip install pelican

If you have the sources, you can install pelican using the distutils command
install. I recommend to do so in a virtualenv::

    $ virtualenv pelican_venv
    $ source bin/activate
    $ python setup.py install

Dependencies
------------

At this time, pelican is dependent of the following python packages:

* feedgenerator, to generate the ATOM feeds.
* jinja2, for templating support.

If you're not using python 2.7, you will also need `argparse`.

Optionally:

* docutils, for reST support
* pygments, to have syntactic colorization with resT input
* Markdown, for Markdown as an input format

Writing articles using pelican
==============================

Files metadata
--------------

Pelican tries to be smart enough to get the informations it needs from the
file system (for instance, about the category of your articles), but you need to
provide by hand some of those informations in your files.

You could provide the metadata in the restructured text files, using the
following syntax (give your file the `.rst` extension)::

    My super title
    ##############

    :date: 2010-10-03 10:20
    :tags: thats, awesome
    :category: yeah
    :author: Alexis Metaireau


You can also use a markdown syntax (with a file ending in `.md`)::

    Date: 2010-12-03
    Title: My super title

    Put you content here.

Note that none of those are mandatory: if the date is not specified, pelican will
rely on the mtime of your file, and the category can also be determined by the
directory where the rst file is. For instance, the category of
`python/foobar/myfoobar.rst` is `foobar`.

Generate your blog
------------------

To launch pelican, just use the `pelican` command::

    $ pelican /path/to/your/content/ [-s path/to/your/settings.py]

And… that's all! You can see your weblog generated on the `content/` folder.

This one will just generate a simple output, with the default theme. It's not
really sexy, as it's a simple HTML output (without any style).

You can create your own style if you want, have a look to the help to see all
the options you can use::

    $ pelican --help

Kickstart a blog
----------------

You also can use the `pelican-quickstart` script to start a new blog in
seconds, by just answering few questions. Just run `pelican-quickstart` and
you're done! (Added in pelican 3)

Pages
-----

If you create a folder named `pages`, all the files in it will be used to
generate static pages.

Then, use the `DISPLAY_PAGES_ON_MENU` setting, which will add all the pages to 
the menu.

Importing an existing blog
--------------------------

It is possible to import your blog from dotclear, wordpress and an RSS feed using 
a simple script. See :ref:`import`.

Translations
------------

It is possible to translate articles. To do so, you need to add a `lang` meta
in your articles/pages, and to set a `DEFAULT_LANG` setting (which is en by
default). 
Then, only articles with this default language will be listed, and
each article will have a translation list.

Pelican uses the "slug" of two articles to compare if they are translations of
each others. So it's possible to define (in restructured text) the slug
directly.

Here is an exemple of two articles (one in english and the other one in
french).

The english one::

    Foobar is not dead
    ##################

    :slug: foobar-is-not-dead
    :lang: en

    That's true, foobar is still alive !

And the french one::

    Foobar n'est pas mort !
    #######################

    :slug: foobar-is-not-dead
    :lang: fr

    Oui oui, foobar est toujours vivant !

Despite the text quality, you can see that only the slug is the same here.
You're not forced to define the slug that way, and it's completely possible to
have two translations with the same title (which defines the slug)

Syntactic recognition
---------------------

Pelican is able to regognise the syntax you are using, and to colorize the
right way your block codes. To do so, you have to use the following syntax::

    .. code-block:: identifier

       your code goes here

The identifier is one of the lexers available `here
<http://pygments.org/docs/lexers/>`_.

You also can use the default `::` syntax::

    ::
        
        your code goes here

It will be assumed that your code is witten in python.

Autoreload
----------

It's possible to tell pelican to watch for your modifications, instead of
manually launching it each time you need. Use the `-r` option, or
`--autoreload`.

Publishing drafts
-----------------

If you want to publish an article as a draft, for friends to review it for
instance, you can add a ``status: draft`` to its metadata, it will then be
available under the ``drafts`` folder, and not be listed under the index page nor
any category page.

Viewing the generated files
---------------------------

The files generated by pelican are static files, so you don't actually need
something special to see what's hapenning with the generated files.

You can either run your browser on the files on your disk::

    $ firefox output/index.html

Or run a simple web server using python::

    cd output && python -m SimpleHTTPServer
