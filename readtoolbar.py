# Copyright (C) 2008, James Simmons.
# Adapted from code Copyright (C) Red Hat Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import logging
from gettext import gettext as _
import re

from gi.repository import Pango
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.menuitem import MenuItem
from sugar3.graphics.toolcombobox import ToolComboBox
from sugar3.graphics.combobox import ComboBox
from sugar3.activity import activity
from sugar3.activity import widgets
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from speech import SpeechManager


class ReadToolbar(Gtk.Toolbar):
    __gtype_name__ = 'ReadToolbar'

    def __init__(self):
        Gtk.Toolbar.__init__(self)

        self.back = ToolButton('go-previous')
        self.back.set_tooltip(_('Back'))
        self.back.props.sensitive = False
        palette = self.back.get_palette()
        self.prev_page = MenuItem(text_label= _("Previous page"))
        palette.menu.append(self.prev_page) 
        self.prev_page.show_all()        
        self.prev_bookmark = MenuItem(text_label= _("Previous bookmark"))
        palette.menu.append(self.prev_bookmark) 
        self.prev_bookmark.show_all()
        self.back.connect('clicked', self.go_back_cb)
        self.prev_page.connect('activate', self.go_back_cb)
        self.prev_bookmark.connect('activate', self.prev_bookmark_activate_cb)
        self.insert(self.back, -1)
        self.back.show()

        self.forward = ToolButton('go-next')
        self.forward.set_tooltip(_('Forward'))
        self.forward.props.sensitive = False
        palette = self.forward.get_palette()
        self.next_page = MenuItem(text_label= _("Next page"))
        palette.menu.append(self.next_page) 
        self.next_page.show_all()        
        self.next_bookmark = MenuItem(text_label= _("Next bookmark"))
        palette.menu.append(self.next_bookmark) 
        self.next_bookmark.show_all()
        self.forward.connect('clicked', self.go_forward_cb)
        self.next_page.connect('activate', self.go_forward_cb)
        self.next_bookmark.connect('activate', self.next_bookmark_activate_cb)
        self.insert(self.forward, -1)
        self.forward.show()

        num_page_item = Gtk.ToolItem()

        self.num_page_entry = Gtk.Entry()
        self.num_page_entry.set_text('0')
        self.num_page_entry.set_alignment(1)
        self.num_page_entry.connect('insert-text',
                                     self.num_page_entry_insert_text_cb)
        self.num_page_entry.connect('activate',
                                     self.num_page_entry_activate_cb)

        self.num_page_entry.set_width_chars(4)

        num_page_item.add(self.num_page_entry)
        self.num_page_entry.show()

        self.insert(num_page_item, -1)
        num_page_item.show()

        total_page_item = Gtk.ToolItem()

        self.total_page_label = Gtk.Label()
        self.total_page_label.set_markup("<span size='14000' foreground='black'>")

        self.total_page_label.set_text(' / 0')
        total_page_item.add(self.total_page_label)
        self.total_page_label.show()

        self.insert(total_page_item, -1)
        total_page_item.show()

        spacer = Gtk.SeparatorToolItem()
        self.insert(spacer, -1)
        spacer.show()
  
        bookmarkitem = Gtk.ToolItem()
        self.bookmarker = ToggleToolButton('emblem-favorite')
        self.bookmarker.set_tooltip(_('Toggle Bookmark'))
        self.bookmarker_handler_id = self.bookmarker.connect('clicked',
                                      self.bookmarker_clicked_cb)
  
        bookmarkitem.add(self.bookmarker)

        self.insert(bookmarkitem, -1)
        bookmarkitem.show_all()

        underline_item = Gtk.ToolItem()
        self.underline = ToggleToolButton('format-text-underline')
        self.underline.set_tooltip(_('Underline'))
        self.underline.props.sensitive = False
        self.underline_id = self.underline.connect('clicked', self.underline_cb)
        underline_item.add(self.underline)
        self.insert(underline_item, -1)
        underline_item.show_all()

    def num_page_entry_insert_text_cb(self, entry, text, length, position):
        if not re.match('[0-9]', text):
            entry.emit_stop_by_name('insert-text')
            return True
        return False

    def num_page_entry_activate_cb(self, entry):
        if entry.props.text:
            page = int(entry.props.text) - 1
        else:
            page = 0

        if page >= self.total_pages:
            page = self.total_pages - 1
        elif page < 0:
            page = 0

        self.current_page = page
        self.activity.set_current_page(page)
        self.activity.show_page(page)
        entry.props.text = str(page + 1)
        self.update_nav_buttons()
        
    def go_back_cb(self, button):
        self.activity.page_previous()
    
    def go_forward_cb(self, button):
        self.activity.page_next()
    
    def update_nav_buttons(self):
        current_page = self.current_page
        self.back.props.sensitive = current_page > 0
        self.forward.props.sensitive = \
            current_page < self.total_pages - 1
        
        self.num_page_entry.props.text = str(current_page + 1)
        self.total_page_label.props.label = \
            ' / ' + str(self.total_pages)

    def set_total_pages(self, pages):
        self.total_pages = pages
        
    def set_current_page(self, page):
        self.current_page = page
        self.update_nav_buttons()
        
    def set_activity(self, activity):
        self.activity = activity

    def prev_bookmark_activate_cb(self, menuitem):
        self.activity.prev_bookmark()
 
    def next_bookmark_activate_cb(self, menuitem):
        self.activity.next_bookmark()
        
    def bookmarker_clicked_cb(self, button):
        self.activity.bookmarker_clicked(button)

    def underline_cb(self, button):
        self.activity.underline_clicked(button)

    def setToggleButtonState(self,button,b,id):
        button.handler_block(id)
        button.set_active(b)
        button.handler_unblock(id)
        
    def update_underline_button(self,  state):
        self.setToggleButtonState(self.underline,  state,  self.underline_id)

    def update_bookmark_button(self,  state):
        self.setToggleButtonState(self.bookmarker,  state,  self.bookmarker_handler_id)

class ViewToolbar(Gtk.Toolbar):
    __gtype_name__ = 'ViewToolbar'

    __gsignals__ = {
        'needs-update-size': (GObject.SIGNAL_RUN_FIRST,
                              GObject.TYPE_NONE,
                              ([])),
        'go-fullscreen': (GObject.SIGNAL_RUN_FIRST,
                          GObject.TYPE_NONE,
                          ([]))
    }

    def __init__(self):
        Gtk.Toolbar.__init__(self)
        self.zoom_out = ToolButton('zoom-out')
        self.zoom_out.set_tooltip(_('Zoom out'))
        self.zoom_out.connect('clicked', self.zoom_out_cb)
        self.insert(self.zoom_out, -1)
        self.zoom_out.show()

        self.zoom_in = ToolButton('zoom-in')
        self.zoom_in.set_tooltip(_('Zoom in'))
        self.zoom_in.connect('clicked', self.zoom_in_cb)
        self.insert(self.zoom_in, -1)
        self.zoom_in.show()

        spacer = Gtk.SeparatorToolItem()
        spacer.props.draw = False
        self.insert(spacer, -1)
        spacer.show()

        self.fullscreen = ToolButton('view-fullscreen')
        self.fullscreen.set_tooltip(_('Fullscreen'))
        self.fullscreen.connect('clicked', self.fullscreen_cb)
        self.insert(self.fullscreen, -1)
        self.fullscreen.show()

    def zoom_in_cb(self, button):
        self.activity.font_increase()
    
    def zoom_out_cb(self, button):
        self.activity.font_decrease()

    def set_activity(self, activity):
        self.activity = activity

    def fullscreen_cb(self, button):
        self.emit('go-fullscreen')

class EditToolbar(widgets.EditToolbar):
    __gtype_name__ = 'EditToolbar'

    def __init__(self):
        widgets.EditToolbar.__init__(self)
        separator = Gtk.SeparatorToolItem()
        separator.set_draw(False)
        separator.set_expand(True)
        self.insert(separator, -1)
        separator.show()

        search_item = Gtk.ToolItem()

        self.search_entry = Gtk.Entry()
        self.search_entry.connect('activate', self.search_entry_activate_cb)

        width = int(Gdk.Screen.width() / 3)
        self.search_entry.set_size_request(width, -1)

        self.search_entry.props.sensitive = False
        
        search_item.add(self.search_entry)
        self.search_entry.show()

        self.insert(search_item, -1)
        search_item.show()

        self.prev = ToolButton('go-previous-paired')
        self.prev.set_tooltip(_('Previous'))
        self.prev.props.sensitive = False
        self.prev.connect('clicked', self.find_prev_cb)
        self.insert(self.prev, -1)
        self.prev.show()

        self.next = ToolButton('go-next-paired')
        self.next.set_tooltip(_('Next'))
        self.next.props.sensitive = False
        self.next.connect('clicked', self.find_next_cb)
        self.insert(self.next, -1)
        self.next.show()

    def set_activity(self, activity):
        self.activity = activity

    def enable_search(self,  state):
        self.search_entry.props.sensitive = state

    def search_entry_activate_cb(self, entry):
        current_page = self.activity.get_current_page()
        self.activity.find_begin(entry.props.text)
        self.update_find_buttons()

    def find_changed_cb(self, page, spec):
        self.update_find_buttons()
        
    def find_prev_cb(self, button):
        self.activity.find_previous()
    
    def find_next_cb(self, button):
        self.activity.find_next()

    def update_find_buttons(self):
        self.prev.props.sensitive = self.activity.can_find_previous()
        self.next.props.sensitive = self.activity.can_find_next()

class BooksToolbar(Gtk.Toolbar):
    __gtype_name__ = 'BooksToolbar'

    def __init__(self):
        Gtk.Toolbar.__init__(self)
        book_search_item = Gtk.ToolItem()

        self.search_entry = Gtk.Entry()
        self.search_entry.connect('activate', self.search_entry_activate_cb)
        self.search_entry.connect("key_press_event", self.keypress_cb)

        width = int(Gdk.Screen.width() / 2)
        self.search_entry.set_size_request(width, -1)

        book_search_item.add(self.search_entry)
        self.search_entry.show()
        self.search_entry.grab_focus()

        self.insert(book_search_item, -1)
        book_search_item.show()

        self.download = ToolButton('go-down')
        self.download.set_tooltip(_('Get Book'))
        self.download.props.sensitive = False
        self.download.connect('clicked', self.get_book_cb)
        self.insert(self.download, -1)
        self.download.show()

        self.hide_results = ToolButton('dialog-cancel')
        self.hide_results.set_tooltip(_('Remove Results List'))
        self.hide_results.props.sensitive = False
        self.hide_results.connect('clicked', self.hide_results_cb)
        self.insert(self.hide_results, -1)
        self.hide_results.show()

    def set_activity(self, activity):
        self.activity = activity

    def search_entry_activate_cb(self, entry):
        self.activity.find_books(entry.props.text)
        self.hide_results.props.sensitive = True

    def get_book_cb(self, button):
        self.activity.get_book()
 
    def enable_button(self,  state):
        self.download.props.sensitive = state
 
    def hide_results_cb(self,  button):
        self.activity.list_scroller.hide()
        self.hide_results.props.sensitive = False
    
    def keypress_cb(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            self.activity.list_scroller.hide()
            self.hide_results.props.sensitive = False
            return True

class SpeechToolbar(Gtk.Toolbar):
    def __init__(self):
        Gtk.Toolbar.__init__(self)
        self.activity = None
        self._speech = SpeechManager()
        self._voices = self._speech.get_all_voices() # a dictionary

        locale = os.environ.get('LANG', '')
        language_location = locale.split('.', 1)[0].lower()
        language = language_location.split('_')[0]
        # if the language is es but not es_es default to es_la (latin voice) 
        if language == 'es' and language_location != 'es_es':
            language_location = 'es_la'

        self._voice = 'en_us'
        if language_location in self._voices:
            self._voice = language_location
        elif language in self._voices:
            self._voice = language

        voice_names = []
        for language, name in self._voices.iteritems():
            voice_names.append((language, name))
        voice_names.sort(self._compare_voices)

        # Play button Image
        play_img = Gtk.Image()
        play_img.show()
        play_img.set_from_icon_name('media-playback-start',
                Gtk.IconSize.LARGE_TOOLBAR)

        # Pause button Image
        pause_img = Gtk.Image()
        pause_img.show()
        pause_img.set_from_icon_name('media-playback-pause',
                Gtk.IconSize.LARGE_TOOLBAR)

        # Play button
        self.play_button = ToggleToolButton('media-playback-start')
        self.play_button.show()
        self.play_button.connect('toggled', self._play_toggled_cb, [play_img, pause_img])
        self.insert(self.play_button, -1)
        self.play_button.set_tooltip(_('Play / Pause'))

        combo = ComboBox()
        which = 0
        for pair in voice_names:
            language, name = pair
            combo.append_item(language, name)
            if language == self._voice:
                combo.set_active(which)
            which += 1

        combo.connect('changed', self._voice_changed_cb)
        combotool = ToolComboBox(combo)
        self.insert(combotool, -1)
        combotool.show()

        self.pitchadj = Gtk.Adjustment(0, -100, 100, 1, 10, 0)
        pitchbar = Gtk.HScale()
        pitchbar.set_adjustment(self.pitchadj)
        pitchbar.set_draw_value(False)
        # pitchbar.set_update_policy(Gtk.UpdatePolicy.ALWAYS)
        pitchbar.set_size_request(150,15)
        pitchtool = Gtk.ToolItem()
        pitchtool.add(pitchbar)
        pitchtool.show()
        self.insert(pitchtool, -1)
        pitchbar.show()

        self.rateadj = Gtk.Adjustment(0, -100, 100, 1, 10, 0)
        ratebar = Gtk.HScale()
        ratebar.set_adjustment(self.rateadj)
        ratebar.set_draw_value(False)
        #ratebar.set_update_policy(Gtk.UpdatePolicy.ALWAYS)
        ratebar.set_size_request(150,15)
        ratetool = Gtk.ToolItem()
        ratetool.add(ratebar)
        ratetool.show()
        self.insert(ratetool, -1)
        ratebar.show()

    def _compare_voices(self, a, b):
        if a[1].lower() == b[1].lower():
            return 0
        if a[1].lower() < b[1].lower():
            return -1
        if a[1].lower() > b[1].lower():
            return 1
        
    def _voice_changed_cb(self, combo):
        self._voice = combo.props.value
        self._speech.say_text(self._voices[self._voice])

    def pitch_adjusted_cb(self, get):
        self._speech.set_pitch(int(get.get_value()))
        self._speech.say_text(_("pitch adjusted"))
        f = open(os.path.join(self.activity.get_activity_root(), 'instance',  'pitch.txt'),  'w')
        try:
            f.write(str(self._speech.get_pitch()))
        finally:
            f.close()

    def rate_adjusted_cb(self, get):
        self._speech.set_rate(int(get.get_value()))
        self._speech.say_text(_("rate adjusted"))
        f = open(os.path.join(self.activity.get_activity_root(), 'instance',  'rate.txt'),  'w')
        try:
            f.write(str(self._speech.get_rate()))
        finally:
            f.close()
      
    def set_activity(self, activity):
        self.activity = activity
        if os.path.exists(os.path.join(activity.get_activity_root(), 'instance',  'pitch.txt')):
            f = open(os.path.join(activity.get_activity_root(), 'instance',  'pitch.txt'),  'r')
            line = f.readline()
            pitch = int(line.strip())
            self.pitchadj.set_value(pitch)
            self._speech.set_pitch(pitch)
            f.close()
        if os.path.exists(os.path.join(activity.get_activity_root(), 'instance',  'rate.txt')):
            f = open(os.path.join(activity.get_activity_root(), 'instance',  'rate.txt'),  'r')
            line = f.readline()
            rate = int(line.strip())
            self.rateadj.set_value(rate)
            self._speech.set_rate(rate)
            f.close()
        self.pitchadj.connect("value_changed", self.pitch_adjusted_cb)
        self.rateadj.connect("value_changed", self.rate_adjusted_cb)
    
    def _play_toggled_cb(self, widget, images):
        widget.set_icon_widget(images[int(widget.get_active())])

        if widget.get_active():
            self.play_button.set_icon_name('media-playback-pause')
            self._speech.say_text(
            self.activity.add_word_marks(),
                lang_code=self._voice)
        else:
            self.play_button.set_icon_name('media-playback-start')
            self._speech.pause()

    def is_playing(self):
        self._speech.get_is_playing()

    def stop(self):
        self._speech.stop()
