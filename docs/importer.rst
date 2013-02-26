.. _import:

=================================
 Import from other blog software
=================================


Description
===========

``pelican-import`` is a command-line tool for converting articles from other
software to ReStructuredText or Markdown. The supported import formats are:

- WordPress XML export
- Dotclear export
- RSS/Atom feed

The conversion from HTML to reStructuredText or Markdown relies on `Pandoc`_.
For Dotclear, if the source posts are written with Markdown syntax, they will
not be converted (as Pelican also supports Markdown).


Dependencies
============

``pelican-import`` has some dependencies not required by the rest of pelican:

- *BeautifulSoup*, for WordPress and Dotclear import. Can be installed like
  any other Python package (``pip install BeautifulSoup``).
- *Feedparser*, for feed import (``pip install feedparser``).
- *Pandoc*, see the `Pandoc site`_ for installation instructions on your
  operating system.

.. _Pandoc: http://johnmacfarlane.net/pandoc/
.. _Pandoc site: http://johnmacfarlane.net/pandoc/installing.html


Usage
=====

::

    pelican-import [-h] [--wpfile] [--dotclear] [--feed] [-o OUTPUT]
                   [-m MARKUP] [--dir-cat] [--strip-raw] [--disable-slugs]
                   input

Positional arguments
--------------------

  input                 The input file to read

Optional arguments
------------------

  -h, --help            Show this help message and exit
  --wpfile              WordPress XML export (default: False)
  --dotclear            Dotclear export (default: False)
  --feed                Feed to parse (default: False)
  -o OUTPUT, --output OUTPUT
                        Output path (default: output)
  -m MARKUP, --markup MARKUP
                        Output markup format (supports rst & markdown)
                        (default: rst)
  --dir-cat             Put files in directories with categories name
                        (default: False)
  --strip-raw           Strip raw HTML code that can't be converted to markup
                        such as flash embeds or iframes (wordpress import
                        only) (default: False)
  --disable-slugs       Disable storing slugs from imported posts within
                        output. With this disabled, your Pelican URLs may not
                        be consistent with your original posts. (default:
                        False)


Examples
========

For WordPress::

    $ pelican-import --wpfile -o ~/output ~/posts.xml

For Dotclear::

    $ pelican-import --dotclear -o ~/output ~/backup.txt


Tests
=====

To test the module, one can use sample files:

- for WordPress: http://wpcandy.com/made/the-sample-post-collection
- for Dotclear: http://themes.dotaddict.org/files/public/downloads/lorem-backup.txt
