# -*- coding: utf-8 -*-

from mock import MagicMock
import os
import re

from pelican.generators import ArticlesGenerator, LessCSSGenerator, PagesGenerator
from pelican.settings import _DEFAULT_CONFIG
from .support import unittest, temporary_folder, skipIfNoExecutable

CUR_DIR = os.path.dirname(__file__)


class TestArticlesGenerator(unittest.TestCase):

    def test_generate_feeds(self):

        generator = ArticlesGenerator(None, {'FEED': _DEFAULT_CONFIG['FEED']},
                                      None, _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        writer = MagicMock()
        generator.generate_feeds(writer)
        writer.write_feed.assert_called_with([], None, 'feeds/all.atom.xml')

        generator = ArticlesGenerator(None, {'FEED': None}, None,
                                      _DEFAULT_CONFIG['THEME'], None, None)
        writer = MagicMock()
        generator.generate_feeds(writer)
        self.assertFalse(writer.write_feed.called)

    def test_generate_context(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['ARTICLE_DIR'] = 'content'
        settings['DEFAULT_CATEGORY'] = 'Default'
        generator = ArticlesGenerator(settings.copy(), settings, CUR_DIR,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        generator.generate_context()
        for article in generator.articles:
            relfilepath = os.path.relpath(article.filename, CUR_DIR)
            if relfilepath == os.path.join("TestCategory",
                                           "article_with_category.rst"):
                self.assertEquals(article.category.name, 'yeah')
            elif relfilepath == os.path.join("TestCategory",
                                             "article_without_category.rst"):
                self.assertEquals(article.category.name, 'TestCategory')
            elif relfilepath == "article_without_category.rst":
                self.assertEquals(article.category.name, 'Default')

        categories = [cat.name for cat, _ in generator.categories]
        # assert that the categories are ordered as expected
        self.assertEquals(
                categories, ['Default', 'TestCategory', 'Yeah', 'test',
                             'yeah'])

    def test_direct_templates_save_as_default(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['DIRECT_TEMPLATES'] = ['archives']
        generator = ArticlesGenerator(settings.copy(), settings, None,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives.html",
            generator.get_template("archives"), settings,
            blog=True, paginated={}, page_name='archives')

    def test_direct_templates_save_as_modified(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        generator = ArticlesGenerator(settings, settings, None,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_with("archives/index.html",
            generator.get_template("archives"), settings,
            blog=True, paginated={}, page_name='archives')

    def test_direct_templates_save_as_false(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['DIRECT_TEMPLATES'] = ['archives']
        settings['ARCHIVES_SAVE_AS'] = 'archives/index.html'
        generator = ArticlesGenerator(settings, settings, None,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        write = MagicMock()
        generator.generate_direct_templates(write)
        write.assert_called_count == 0


class TestPageGenerator(unittest.TestCase):
    """
    Every time you want to test for a new field;
    Make sure the test pages in "TestPages" have all the fields
    Add it to distilled in distill_pages
    Then update the assertItemsEqual in test_generate_context to match expected
    """

    def distill_pages(self, pages):
        distilled = []
        for page in pages:
           distilled.append([
                    page.title,
                    page.status
                ]
           )
        return distilled

    def test_generate_context(self):
        settings = _DEFAULT_CONFIG.copy()

        settings['PAGE_DIR'] = 'TestPages'
        generator = PagesGenerator(settings.copy(), settings, CUR_DIR,
                                      _DEFAULT_CONFIG['THEME'], None,
                                      _DEFAULT_CONFIG['MARKUP'])
        generator.generate_context()
        pages = self.distill_pages(generator.pages)
        hidden_pages = self.distill_pages(generator.hidden_pages)

        pages_expected = [
            [u'This is a test page', 'published'],
            [u'This is a markdown test page', 'published']
        ]
        hidden_pages_expected = [
            [u'This is a test hidden page', 'hidden'],
            [u'This is a markdown test hidden page', 'hidden']
        ]

        self.assertItemsEqual(pages_expected,pages)
        self.assertItemsEqual(hidden_pages_expected,hidden_pages)


class TestLessCSSGenerator(unittest.TestCase):

    LESS_CONTENT = """
        @color: #4D926F;

        #header {
          color: @color;
        }
        h2 {
          color: @color;
        }
    """

    @skipIfNoExecutable('lessc')
    def test_less_compiler(self):

        settings = _DEFAULT_CONFIG.copy()
        settings['STATIC_PATHS'] = ['static']
        settings['LESS_GENERATOR'] = True

        # we'll nest here for py < 2.7 compat
        with temporary_folder() as temp_content:
            with temporary_folder() as temp_output:
                generator = LessCSSGenerator(None, settings, temp_content,
                                _DEFAULT_CONFIG['THEME'], temp_output, None)

                # create a dummy less file
                less_dir = os.path.join(temp_content, 'static', 'css')
                less_filename = os.path.join(less_dir, 'test.less')

                less_output = os.path.join(temp_output, 'static', 'css',
                                    'test.css')

                os.makedirs(less_dir)
                with open(less_filename, 'w') as less_file:
                    less_file.write(self.LESS_CONTENT)

                generator.generate_output()

                # we have the file ?
                self.assertTrue(os.path.exists(less_output))

                # was it compiled ?
                self.assertIsNotNone(re.search(r'^\s+color:\s*#4D926F;$',
                    open(less_output).read(), re.MULTILINE | re.IGNORECASE))
