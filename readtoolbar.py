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

import logging
from gettext import gettext as _
import re

import pango
import gobject
import gtk

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.graphics.combobox import ComboBox
from sugar.activity import activity
from sugar.graphics.toggletoolbutton import ToggleToolButton

import speech

class ReadToolbar(gtk.Toolbar):
    __gtype_name__ = 'ReadToolbar'

    def __init__(self):
        gtk.Toolbar.__init__(self)

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

        num_page_item = gtk.ToolItem()

        self.num_page_entry = gtk.Entry()
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

        total_page_item = gtk.ToolItem()

        self.total_page_label = gtk.Label()

        label_attributes = pango.AttrList()
        label_attributes.insert(pango.AttrSize(14000, 0, -1))
        label_attributes.insert(pango.AttrForeground(65535, 65535, 65535, 0, -1))
        self.total_page_label.set_attributes(label_attributes)

        self.total_page_label.set_text(' / 0')
        total_page_item.add(self.total_page_label)
        self.total_page_label.show()

        self.insert(total_page_item, -1)
        total_page_item.show()

        spacer = gtk.SeparatorToolItem()
        self.insert(spacer, -1)
        spacer.show()
  
        bookmarkitem = gtk.ToolItem()
        self.bookmarker = ToggleToolButton('emblem-favorite')
        self.bookmarker.set_tooltip(_('Toggle Bookmark'))
        self.bookmarker_handler_id = self.bookmarker.connect('clicked',
                                      self.bookmarker_clicked_cb)
  
        bookmarkitem.add(self.bookmarker)

        self.insert(bookmarkitem, -1)
        bookmarkitem.show_all()

        underline_item = gtk.ToolItem()
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

class ViewToolbar(gtk.Toolbar):
    __gtype_name__ = 'ViewToolbar'

    __gsignals__ = {
        'needs-update-size': (gobject.SIGNAL_RUN_FIRST,
                              gobject.TYPE_NONE,
                              ([])),
        'go-fullscreen': (gobject.SIGNAL_RUN_FIRST,
                          gobject.TYPE_NONE,
                          ([]))
    }

    def __init__(self):
        gtk.Toolbar.__init__(self)
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

        spacer = gtk.SeparatorToolItem()
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

class EditToolbar(activity.EditToolbar):
    __gtype_name__ = 'EditToolbar'

    def __init__(self):
        activity.EditToolbar.__init__(self)
        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        separator.set_expand(True)
        self.insert(separator, -1)
        separator.show()

        search_item = gtk.ToolItem()

        self.search_entry = gtk.Entry()
        self.search_entry.connect('activate', self.search_entry_activate_cb)

        width = int(gtk.gdk.screen_width() / 3)
        self.search_entry.set_size_request(width, -1)

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

class BooksToolbar(gtk.Toolbar):
    __gtype_name__ = 'BooksToolbar'

    def __init__(self):
        gtk.Toolbar.__init__(self)
        book_search_item = gtk.ToolItem()

        self.search_entry = gtk.Entry()
        self.search_entry.connect('activate', self.search_entry_activate_cb)
        self.search_entry.connect("key_press_event", self.keypress_cb)

        width = int(gtk.gdk.screen_width() / 2)
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
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            self.activity.list_scroller.hide()
            self.hide_results.props.sensitive = False
            return True

class   SpeechToolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)
        voicebar = gtk.Toolbar()
        self.activity = None
        self.sorted_voices = [i for i in speech.voices()]
        self.sorted_voices.sort(self.compare_voices)
        default = 0
        for voice in self.sorted_voices:
            if voice[0] == 'default':
                break
            default = default + 1

        # Play button Image
        play_img = gtk.Image()
        play_img.show()
        play_img.set_from_icon_name('media-playback-start',
                gtk.ICON_SIZE_LARGE_TOOLBAR)

        # Pause button Image
        pause_img = gtk.Image()
        pause_img.show()
        pause_img.set_from_icon_name('media-playback-pause',
                gtk.ICON_SIZE_LARGE_TOOLBAR)

        # Play button
        self.play_btn = ToggleToolButton('media-playback-start')
        self.play_btn.show()
        self.play_btn.connect('toggled', self.play_cb, [play_img, pause_img])
        self.insert(self.play_btn, -1)
        self.play_btn.set_tooltip(_('Play / Pause'))

        self.voice_combo = ComboBox()
        self.voice_combo.connect('changed', self.voice_changed_cb)
        for voice in self.sorted_voices:
            self.voice_combo.append_item(voice, voice[0])
        self.voice_combo.set_active(default)
        combotool = ToolComboBox(self.voice_combo)
        self.insert(combotool, -1)
        combotool.show()

        self.pitchadj = gtk.Adjustment(0, -100, 100, 1, 10, 0)
        self.pitchadj.connect("value_changed", self.pitch_adjusted_cb)
        pitchbar = gtk.HScale(self.pitchadj)
        pitchbar.set_draw_value(False)
        pitchbar.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        pitchbar.set_size_request(150,15)
        pitchtool = gtk.ToolItem()
        pitchtool.add(pitchbar)
        pitchtool.show()
        self.insert(pitchtool, -1)
        pitchbar.show()

        self.rateadj = gtk.Adjustment(0, -100, 100, 1, 10, 0)
        self.rateadj.connect("value_changed", self.rate_adjusted_cb)
        ratebar = gtk.HScale(self.rateadj)
        ratebar.set_draw_value(False)
        ratebar.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        ratebar.set_size_request(150,15)
        ratetool = gtk.ToolItem()
        ratetool.add(ratebar)
        ratetool.show()
        self.insert(ratetool, -1)
        ratebar.show()

    def compare_voices(self,  a,  b):
        if a[0].lower() == b[0].lower():
            return 0
        if a[0] .lower()< b[0].lower():
            return -1
        if a[0] .lower()> b[0].lower():
            return 1
        
    def voice_changed_cb(self, combo):
        speech.voice = combo.props.value
        if self.activity != None:
            speech.say(speech.voice[0])

    def pitch_adjusted_cb(self, get):
        speech.pitch = int(get.value)
        speech.say(_("pitch adjusted"))

    def rate_adjusted_cb(self, get):
        speech.rate = int(get.value)
        speech.say(_("rate adjusted"))
      
    def set_activity(self, activity):
        self.activity = activity
    
    def play_cb(self, widget, images):
        widget.set_icon_widget(images[int(widget.get_active())])

        if widget.get_active():
            if speech.is_stopped():
                speech.play(self.activity.add_word_marks())
        else:
            speech.stop()
            self.activity.show_underlines()
