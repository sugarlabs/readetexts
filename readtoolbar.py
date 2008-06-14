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

try:
    import speechd
except:
    print "Speech not supported"

class ReadToolbar(gtk.Toolbar):
    __gtype_name__ = 'ReadToolbar'

    def __init__(self):
        gtk.Toolbar.__init__(self)
        self._back = ToolButton('go-previous')
        self._back.set_tooltip(_('Back'))
        self._back.props.sensitive = False
        self._back.connect('clicked', self._go_back_cb)
        self.insert(self._back, -1)
        self._back.show()

        self._forward = ToolButton('go-next')
        self._forward.set_tooltip(_('Forward'))
        self._forward.props.sensitive = False
        self._forward.connect('clicked', self._go_forward_cb)
        self.insert(self._forward, -1)
        self._forward.show()

        num_page_item = gtk.ToolItem()

        self._num_page_entry = gtk.Entry()
        self._num_page_entry.set_text('0')
        self._num_page_entry.set_alignment(1)
        self._num_page_entry.connect('insert-text',
                                     self._num_page_entry_insert_text_cb)
        self._num_page_entry.connect('activate',
                                     self._num_page_entry_activate_cb)

        self._num_page_entry.set_width_chars(4)

        num_page_item.add(self._num_page_entry)
        self._num_page_entry.show()

        self.insert(num_page_item, -1)
        num_page_item.show()

        total_page_item = gtk.ToolItem()

        self._total_page_label = gtk.Label()

        label_attributes = pango.AttrList()
        label_attributes.insert(pango.AttrSize(14000, 0, -1))
        label_attributes.insert(pango.AttrForeground(65535, 65535, 65535, 0, -1))
        self._total_page_label.set_attributes(label_attributes)

        self._total_page_label.set_text(' / 0')
        total_page_item.add(self._total_page_label)
        self._total_page_label.show()

        self.insert(total_page_item, -1)
        total_page_item.show()

        downloaded_item = gtk.ToolItem()
        self._downloaded_label = gtk.Label()
        self._downloaded_label.set_attributes(label_attributes)

        self._downloaded_label.set_text('')
        downloaded_item.add(self._downloaded_label)
        self._downloaded_label.show()

        self.insert(downloaded_item, -1)
        downloaded_item.show()
 
    def set_downloaded_bytes(self, bytes,  total):
        self._downloaded_label.props.label = '     ' + str(bytes) + ' of ' + str(total) + ' received'

    def _num_page_entry_insert_text_cb(self, entry, text, length, position):
        if not re.match('[0-9]', text):
            entry.emit_stop_by_name('insert-text')
            return True
        return False

    def _num_page_entry_activate_cb(self, entry):
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
        self._update_nav_buttons()
        
    def _go_back_cb(self, button):
        self.activity.page_previous()
    
    def _go_forward_cb(self, button):
        self.activity.page_next()
    
    def _update_nav_buttons(self):
        current_page = self.current_page
        self._back.props.sensitive = current_page > 0
        self._forward.props.sensitive = \
            current_page < self.total_pages - 1
        
        self._num_page_entry.props.text = str(current_page + 1)
        self._total_page_label.props.label = \
            ' / ' + str(self.total_pages)

    def set_total_pages(self, pages):
        self.total_pages = pages
        
    def set_current_page(self, page):
        self.current_page = page
        self._update_nav_buttons()
        
    def set_activity(self, activity):
        self.activity = activity

class ViewToolbar(gtk.Toolbar):
    __gtype_name__ = 'ViewToolbar'

    def __init__(self):
        gtk.Toolbar.__init__(self)
        self._zoom_out = ToolButton('zoom-out')
        self._zoom_out.set_tooltip(_('Zoom out'))
        self._zoom_out.connect('clicked', self._zoom_out_cb)
        self.insert(self._zoom_out, -1)
        self._zoom_out.show()

        self._zoom_in = ToolButton('zoom-in')
        self._zoom_in.set_tooltip(_('Zoom in'))
        self._zoom_in.connect('clicked', self._zoom_in_cb)
        self.insert(self._zoom_in, -1)
        self._zoom_in.show()

    def _zoom_in_cb(self, button):
        self.activity.font_increase()
    
    def _zoom_out_cb(self, button):
        self.activity.font_decrease()

    def set_activity(self, activity):
        self.activity = activity

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

        self._search_entry = gtk.Entry()
        self._search_entry.connect('activate', self._search_entry_activate_cb)

        width = int(gtk.gdk.screen_width() / 3)
        self._search_entry.set_size_request(width, -1)

        search_item.add(self._search_entry)
        self._search_entry.show()

        self.insert(search_item, -1)
        search_item.show()

        self._prev = ToolButton('go-previous-paired')
        self._prev.set_tooltip(_('Previous'))
        self._prev.props.sensitive = False
        self._prev.connect('clicked', self._find_prev_cb)
        self.insert(self._prev, -1)
        self._prev.show()

        self._next = ToolButton('go-next-paired')
        self._next.set_tooltip(_('Next'))
        self._next.props.sensitive = False
        self._next.connect('clicked', self._find_next_cb)
        self.insert(self._next, -1)
        self._next.show()

    def set_activity(self, activity):
        self.activity = activity

    def _search_entry_activate_cb(self, entry):
        current_page = self.activity.get_current_page()
        self.activity.find_begin(entry.props.text)
        self._update_find_buttons()

    def _find_changed_cb(self, page, spec):
        self._update_find_buttons()
        
    def _find_prev_cb(self, button):
        self.activity.find_previous()
    
    def _find_next_cb(self, button):
        self.activity.find_next()

    def _update_find_buttons(self):
        self._prev.props.sensitive = self.activity.can_find_previous()
        self._next.props.sensitive = self.activity.can_find_next()

class   SpeechToolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)
        voicebar = gtk.Toolbar()
        
        client = speechd.SSIPClient('readetextstest')
        voices = client.list_synthesis_voices()
        client.close()
        self.sorted_voices = []
        for voice in voices:
            self.sorted_voices.append(voice)
        self.sorted_voices.sort(self.compare_voices)
        default = 0
        for voice in self.sorted_voices:
            if voice[0] == 'default':
                break
            default = default + 1

        self.voice_combo = ComboBox()
        self.voice_combo.connect('changed', self.voice_changed_cb)
        for voice in self.sorted_voices:
            self.voice_combo.append_item(voice, voice[0])
        self.voice_combo.set_active(default)
        self.selected_voice = self.voice_combo.props.value
        combotool = ToolComboBox(self.voice_combo)
        self.insert(combotool, -1)
        combotool.show()

        self.pitchadj = gtk.Adjustment(0, -100, 100, 1, 10, 0)
        self.pitchadj.connect("value_changed", self.pitch_adjusted_cb, self.pitchadj)
        pitchbar = gtk.HScale(self.pitchadj)
        pitchbar.set_draw_value(False)
        pitchbar.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        pitchbar.set_size_request(240,15)
        pitchtool = gtk.ToolItem()
        pitchtool.add(pitchbar)
        pitchtool.show()
        self.insert(pitchtool, -1)
        pitchbar.show()

        self.rateadj = gtk.Adjustment(0, -100, 100, 1, 10, 0)
        self.rateadj.connect("value_changed", self.rate_adjusted_cb, self.rateadj)
        ratebar = gtk.HScale(self.rateadj)
        ratebar.set_draw_value(False)
        ratebar.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        ratebar.set_size_request(240,15)
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
        self.selected_voice = combo.props.value
        self.activity.set_speech_voice(self.selected_voice)
        self.say(self.selected_voice[0])

    def pitch_adjusted_cb(self, get, data=None):
        self.activity.set_speech_pitch(int(self.pitchadj.value))
        self.say(_("pitch adjusted"))

    def rate_adjusted_cb(self, get, data=None):
        self.activity.set_speech_rate(int(self.rateadj.value))
        self.say(_("rate adjusted"))
      
    def set_activity(self, activity):
        self.activity = activity
        self.activity.set_speech_voice(self.selected_voice)
    
    def say(self,  words):
        client = speechd.SSIPClient('readetextstest')
        client.set_rate(int(self.rateadj.value))
        client.set_pitch(int(self.pitchadj.value))
        client.set_language(self.selected_voice[1])
        client.speak(words)
        client.close()

