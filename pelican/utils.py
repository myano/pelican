# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import six

import os
import re
import pytz
import shutil
import traceback
import logging
import errno
import locale
import fnmatch
from collections import defaultdict, Hashable
from functools import partial

from codecs import open
from datetime import datetime
from itertools import groupby
from jinja2 import Markup
from operator import attrgetter

logger = logging.getLogger(__name__)


def strftime(date, date_format):
    """
    Replacement for the builtin strftime().

    This :func:`strftime()` is compatible to Python 2 and 3. In both cases,
    input and output is always unicode.
        
    Still, Python 3's :func:`strftime()` seems to somehow "normalize" unicode
    chars in the format string. So if e.g. your format string contains 'ø' or
    'ä', the result will be 'o' and 'a'.

    See here for an `extensive testcase <https://github.com/dmdm/test_strftime>`_.

    :param date: Any object that sports a :meth:`strftime()` method.
    :param date_format: Format string, can always be unicode.
    :returns: Unicode string with formatted date.
    """
    # As tehkonst confirmed, above mentioned testcase runs correctly on
    # Python 2 and 3 on Windows as well. Thanks.
    if six.PY3:
        # It could be so easy... *sigh*
        return date.strftime(date_format)
        # TODO Perhaps we should refactor again, so that the
        # xmlcharrefreplace-regex-dance is always done, regardless
        # of the Python version.
    else:
        # We must ensure that the format string is an encoded byte
        # string, ASCII only WTF!!!
        # But with "xmlcharrefreplace" our formatted date will produce
        # *yuck* like this:
        #        "Øl trinken beim Besäufnis"
        #    --> "&#216;l trinken beim Bes&#228;ufnis"
        date_format = date_format.encode('ascii',
            errors="xmlcharrefreplace")
        result = date.strftime(date_format)
        # strftime() returns an encoded byte string
        # which we must decode into unicode.
        lang_code, enc = locale.getlocale(locale.LC_ALL)
        if enc:
            result = result.decode(enc)
        else:
            result = unicode(result)
        # Convert XML character references back to unicode characters.
        if "&#" in result:
            result = re.sub(r'&#(?P<num>\d+);'
                , lambda m: unichr(int(m.group('num')))
                , result
            )
        return result



#----------------------------------------------------------------------------
# Stolen from Django: django.utils.encoding
#

def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if not six.PY3:
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass

#----------------------------------------------------------------------------

class NoFilesError(Exception):
    pass


class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return partial(self.__call__, obj)


def deprecated_attribute(old, new, since=None, remove=None, doc=None):
    """Attribute deprecation decorator for gentle upgrades

    For example:

        class MyClass (object):
            @deprecated_attribute(
                old='abc', new='xyz', since=(3, 2, 0), remove=(4, 1, 3))
            def abc(): return None

            def __init__(self):
                xyz = 5

    Note that the decorator needs a dummy method to attach to, but the
    content of the dummy method is ignored.
    """
    def _warn():
        version = '.'.join(six.text_type(x) for x in since)
        message = ['{} has been deprecated since {}'.format(old, version)]
        if remove:
            version = '.'.join(six.text_type(x) for x in remove)
            message.append(
                ' and will be removed by version {}'.format(version))
        message.append('.  Use {} instead.'.format(new))
        logger.warning(''.join(message))
        logger.debug(''.join(
                six.text_type(x) for x in traceback.format_stack()))

    def fget(self):
        _warn()
        return getattr(self, new)

    def fset(self, value):
        _warn()
        setattr(self, new, value)

    def decorator(dummy):
        return property(fget=fget, fset=fset, doc=doc)

    return decorator

def get_date(string):
    """Return a datetime object from a string.

    If no format matches the given date, raise a ValueError.
    """
    string = re.sub(' +', ' ', string)
    formats = ['%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
               '%Y-%m-%d', '%Y/%m/%d',
               '%d-%m-%Y', '%Y-%d-%m',  # Weird ones
               '%d/%m/%Y', '%d.%m.%Y',
               '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S']
    for date_format in formats:
        try:
            return datetime.strptime(string, date_format)
        except ValueError:
            pass
    raise ValueError("'%s' is not a valid date" % string)


class pelican_open(object):
    """Open a file and return it's content"""
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        return open(self.filename, encoding='utf-8').read()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from django sources.
    """
    # TODO Maybe steal again from current Django 1.5dev
    value = Markup(value).striptags()
    # value must be unicode per se
    import unicodedata
    from unidecode import unidecode
    # unidecode returns str in Py2 and 3, so in Py2 we have to make
    # it unicode again
    value = unidecode(value)
    if isinstance(value, six.binary_type):
        value = value.decode('ascii')
    # still unicode
    value = unicodedata.normalize('NFKD', value)
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    # we want only ASCII chars
    value = value.encode('ascii', 'ignore')
    # but Pelican should generally use only unicode
    return value.decode('ascii')


def copy(path, source, destination, destination_path=None, overwrite=False):
    """Copy path from origin to destination.

    The function is able to copy either files or directories.

    :param path: the path to be copied from the source to the destination
    :param source: the source dir
    :param destination: the destination dir
    :param destination_path: the destination path (optional)
    :param overwrite: whether to overwrite the destination if already exists
                      or not
    """
    if not destination_path:
        destination_path = path

    source_ = os.path.abspath(os.path.expanduser(os.path.join(source, path)))
    destination_ = os.path.abspath(
        os.path.expanduser(os.path.join(destination, destination_path)))

    if os.path.isdir(source_):
        try:
            shutil.copytree(source_, destination_)
            logger.info('copying %s to %s' % (source_, destination_))
        except OSError:
            if overwrite:
                shutil.rmtree(destination_)
                shutil.copytree(source_, destination_)
                logger.info('replacement of %s with %s' % (source_,
                    destination_))

    elif os.path.isfile(source_):
        dest_dir = os.path.dirname(destination_)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy(source_, destination_)
        logger.info('copying %s to %s' % (source_, destination_))
    else:
        logger.warning('skipped copy %s to %s' % (source_, destination_))

def clean_output_dir(path):
    """Remove all the files from the output directory"""

    if not os.path.exists(path):
        logger.debug("Directory already removed: %s" % path)
        return

    if not os.path.isdir(path):
        try:
            os.remove(path)
        except Exception as e:
            logger.error("Unable to delete file %s; %s" % (path, str(e)))
        return

    # remove all the existing content from the output folder
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        if os.path.isdir(file):
            try:
                shutil.rmtree(file)
                logger.debug("Deleted directory %s" % file)
            except Exception as e:
                logger.error("Unable to delete directory %s; %s" % (
                        file, str(e)))
        elif os.path.isfile(file) or os.path.islink(file):
            try:
                os.remove(file)
                logger.debug("Deleted file/link %s" % file)
            except Exception as e:
                logger.error("Unable to delete file %s; %s" % (file, str(e)))
        else:
            logger.error("Unable to delete %s, file type unknown" % file)


def get_relative_path(path):
    """Return the relative path from the given path to the root path."""
    nslashes = path.count('/')
    if nslashes == 0:
        return '.'
    else:
        return '/'.join(['..'] * nslashes)


def truncate_html_words(s, num, end_text='...'):
    """Truncates HTML to a certain number of words (not counting tags and
    comments). Closes opened tags if they were correctly closed in the given
    html. Takes an optional argument of what should be used to notify that the
    string has been truncated, defaulting to ellipsis (...).

    Newlines in the HTML are preserved.
    From the django framework.
    """
    length = int(num)
    if length <= 0:
        return ''
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area',
                      'hr', 'input')

    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U)
    re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    # Count non-HTML words and keep note of open tags
    pos = 0
    end_text_pos = 0
    words = 0
    open_tags = []
    while words <= length:
        m = re_words.search(s, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            if words == length:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or end_text_pos:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        tagname = tagname.lower()  # Element names are always case-insensitive
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag,
                # all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i + 1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)
    if words <= length:
        # Don't try to close tags if we don't need to truncate
        return s
    out = s[:end_text_pos]
    if end_text:
        out += ' ' + end_text
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out


def process_translations(content_list):
    """ Finds all translation and returns tuple with two lists (index,
    translations).  Index list includes items in default language or items
    which have no variant in default language.

    Also, for each content_list item, it sets attribute 'translations'
    """
    content_list.sort(key=attrgetter('slug'))
    grouped_by_slugs = groupby(content_list, attrgetter('slug'))
    index = []
    translations = []

    for slug, items in grouped_by_slugs:
        items = list(items)
        # find items with default language
        default_lang_items = list(filter(attrgetter('in_default_lang'), items))
        len_ = len(default_lang_items)
        if len_ > 1:
            logger.warning('there are %s variants of "%s"' % (len_, slug))
            for x in default_lang_items:
                logger.warning('    {}'.format(x.source_path))
        elif len_ == 0:
            default_lang_items = items[:1]

        if not slug:
            logger.warning((
                    'empty slug for {!r}. '
                    'You can fix this by adding a title or a slug to your '
                    'content'
                    ).format(default_lang_items[0].source_path))
        index.extend(default_lang_items)
        translations.extend([x for x in items if x not in default_lang_items])
        for a in items:
            a.translations = [x for x in items if x != a]
    return index, translations


LAST_MTIME = 0

def files_changed(path, extensions, ignores=[]):
    """Return True if the files have changed since the last check"""

    def file_times(path):
        """Return the last time files have been modified"""
        for root, dirs, files in os.walk(path):
            dirs[:] = [x for x in dirs if x[0] != '.']
            for f in files:
                if any(f.endswith(ext) for ext in extensions) \
                        and not any(fnmatch.fnmatch(f, ignore) for ignore in ignores):
                    yield os.stat(os.path.join(root, f)).st_mtime

    global LAST_MTIME
    try:
        mtime = max(file_times(path))
        if mtime > LAST_MTIME:
            LAST_MTIME = mtime
            return True
    except ValueError:
        raise NoFilesError("No files with the given extension(s) found.")
    return False


FILENAMES_MTIMES = defaultdict(int)


def file_changed(path):
    mtime = os.stat(path).st_mtime
    if FILENAMES_MTIMES[path] == 0:
        FILENAMES_MTIMES[path] = mtime
        return False
    else:
        if mtime > FILENAMES_MTIMES[path]:
            FILENAMES_MTIMES[path] = mtime
            return True
        return False


def set_date_tzinfo(d, tz_name=None):
    """ Date without tzinfo shoudbe utc.
    This function set the right tz to date that aren't utc and don't have
    tzinfo.
    """
    if tz_name is not None:
        tz = pytz.timezone(tz_name)
        return tz.localize(d)
    else:
        return d


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(path):
            raise
