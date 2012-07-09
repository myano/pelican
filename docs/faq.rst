Frequently Asked Questions (FAQ)
################################

Here is a summary of the frequently asked questions for Pelican.

Is it mandatory to have a configuration file?
=============================================

No, it's not. Configuration files are just an easy way to configure Pelican.
For basic operations, it's possible to specify options while invoking Pelican
via the command line. See ``pelican --help`` for more information.

I'm creating my own theme. How do I use Pygments for syntax highlighting?
=========================================================================

Pygments adds some classes to the generated content. These classes are used by
themes to style code syntax highlighting via CSS. Specifically, you can
customize the appearance of your syntax highlighting via the ``.codehilite pre`` 
class in your theme's CSS file. To see how various styles can be used to render
Django code, for example, you can use the demo `on the project website
<http://pygments.org/demo/15101/>`_.

How do I create my own theme?
==============================

Please refer to :ref:`theming-pelican`.

How can I help?
================

There are several ways to help out. First, you can use Pelican and report any
suggestions or problems you might have on `the bugtracker
<https://github.com/ametaireau/pelican/issues>`_.

If you want to contribute, please fork `the git repository
<https://github.com/ametaireau/pelican/>`_, make your changes, and issue
a pull request. I'll review your changes as soon as possible.

You can also contribute by creating themes and improving the documentation.

I want to use Markdown, but I got an error.
===========================================

Markdown is not a hard dependency for Pelican, so you will need to explicitly
install it. You can do so by typing::

    $ (sudo) pip install markdown

In case you don't have pip installed, consider installing it via::

    $ (sudo) easy_install pip
