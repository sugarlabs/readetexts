import types
import unittest

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango  # noqa: E402

from ReadEtextsActivity import ReadEtextsActivity  # noqa: E402
from readtoolbar import ReadToolbar  # noqa: E402


class PageCountTest(unittest.TestCase):
    def assert_page_count(self, label, count):
        self.assertEqual(label.get_text(), ' / %d' % count)
        self.assertTrue(label.get_use_markup())
        attributes = label.get_layout().get_attributes()
        self.assertIsNotNone(attributes)
        iterator = attributes.get_iterator()
        self.assertEqual(iterator.get(Pango.AttrType.SIZE).as_size().size,
                         14000)
        self.assertIsNone(iterator.get(Pango.AttrType.FOREGROUND))

    def test_toolbar_starts_with_formatted_zero(self):
        toolbar = ReadToolbar()
        self.addCleanup(toolbar.destroy)
        self.assert_page_count(toolbar.total_page_label, 0)

    def test_toolbar_keeps_format_after_page_count_changes(self):
        toolbar = ReadToolbar()
        self.addCleanup(toolbar.destroy)
        for count in (1, 17, 203):
            with self.subTest(count=count):
                toolbar.set_total_pages(count)
                toolbar.set_current_page(0)
                self.assert_page_count(toolbar.total_page_label, count)

    def test_activity_navigation_updates_formatted_count(self):
        entry = Gtk.Entry()
        label = Gtk.Label()
        back = Gtk.Button()
        forward = Gtk.Button()
        for widget in (entry, label, back, forward):
            self.addCleanup(widget.destroy)
        activity = types.SimpleNamespace(
            current_page=0, total_pages=17, num_page_entry=entry,
            total_page_label=label, back=back, forward=forward)
        for page in (0, 8, 16):
            with self.subTest(page=page):
                activity.current_page = page
                ReadEtextsActivity.update_nav_buttons(activity)
                self.assertEqual(entry.get_text(), str(page + 1))
                self.assert_page_count(label, 17)
                self.assertEqual(back.get_sensitive(), page > 0)
                self.assertEqual(forward.get_sensitive(), page < 16)


if __name__ == '__main__':
    unittest.main()
