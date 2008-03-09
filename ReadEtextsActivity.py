#! /usr/bin/env python

# Copyright (C) 2008 James D. Simmons
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
import sys
import os
import logging
import tempfile
import time
import zipfile
import pygtk
import gtk
import string
from sugar.activity import activity
from sugar import network
from sugar.datastore import datastore
from readtoolbar import ReadToolbar, ViewToolbar, EditToolbar
from gettext import gettext as _
import pango
import dbus
import gobject
import hippo
import telepathy

_HARDWARE_MANAGER_INTERFACE = 'org.laptop.HardwareManager'
_HARDWARE_MANAGER_SERVICE = 'org.laptop.HardwareManager'
_HARDWARE_MANAGER_OBJECT_PATH = '/org/laptop/HardwareManager'
_PAGE_SIZE = 38
_TOOLBAR_READ = 2
_SOCKET_TYPE_IPv4 = 2
_SOCKET_ACCESS_CONTROL_LOCALHOST = 0

_logger = logging.getLogger('read-activity')

class ReadHTTPRequestHandler(network.ChunkedGlibHTTPRequestHandler):
    def translate_path(self, path):
        return self.server._filepath

class ReadHTTPServer(network.GlibTCPServer):
    def __init__(self, server_address, filepath):
        self._filepath = filepath
        network.GlibTCPServer.__init__(self, server_address, ReadHTTPRequestHandler)

READ_STREAM_SERVICE = 'read-activity-http'

class ReadEtextsActivity(activity.Activity):
    def __init__(self, handle):
        "The entry point to the Activity"
        activity.Activity.__init__(self, handle)
        self.connect("key_press_event", self.keypress_cb)
        
        self._fileserver = None
        self._object_id = handle.object_id
       
        toolbox = activity.ActivityToolbox(self)
        self.set_toolbox(toolbox)
        
        self._edit_toolbar = EditToolbar()
        self._edit_toolbar.undo.props.visible = False
        self._edit_toolbar.redo.props.visible = False
        self._edit_toolbar.separator.props.visible = False
        self._edit_toolbar.copy.set_sensitive(False)
        self._edit_toolbar.copy.connect('clicked', self.edit_toolbar_copy_cb)
        self._edit_toolbar.paste.props.visible = False
        toolbox.add_toolbar(_('Edit'), self._edit_toolbar)
        self._edit_toolbar.set_activity(self)
        self._edit_toolbar.show()
        
        self._read_toolbar = ReadToolbar()
        toolbox.add_toolbar(_('Read'), self._read_toolbar)
        self._read_toolbar.set_activity(self)
        self._read_toolbar.show()

        self._view_toolbar = ViewToolbar()
        toolbox.add_toolbar(_('View'), self._view_toolbar)
        self._view_toolbar.set_activity(self)
        self._view_toolbar.show()

        toolbox.show()
        self.scrolled = gtk.ScrolledWindow()
        self.scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.scrolled.props.shadow_type = gtk.SHADOW_NONE
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_left_margin(50)
        buffer = self.textview.get_buffer()
        buffer.connect("mark-set", self.mark_set_cb)
        self.font_desc = pango.FontDescription("sans 12")
        self.scrolled.add(self.textview)
        self.textview.show()
        self.set_canvas(self.scrolled)
        self.scrolled.show()
        v_adjustment = self.scrolled.get_vadjustment()
        self.clipboard = gtk.Clipboard(display=gtk.gdk.display_get_default(), selection="CLIPBOARD")
        
        # start on the read toolbar
        self.toolbox.set_current_toolbar(_TOOLBAR_READ)
        self.unused_download_tubes = set()
        self._want_document = True
        self.connect("shared", self._shared_cb)
        h = hash(self._activity_id)
        self.port = 1024 + (h % 64511)

        if handle.uri:
            self._load_document(handle.uri)

        if self._shared_activity:
            # We're joining
            if self.get_shared():
                # Already joined for some reason, just get the document
                self._joined_cb(self)
            else:
                # Wait for a successful join before trying to get the document
                self.connect("joined", self._joined_cb)
        # uncomment this and adjust the path for easier testing
        #else:
        #    self._load_document('file:///home/smcv/tmp/test.pdf')
    
    def mark_set_cb(self, textbuffer, iter, textmark):
        if textbuffer.get_has_selection():
            self._edit_toolbar.copy.set_sensitive(True)
        else:
            self._edit_toolbar.copy.set_sensitive(False)

    def edit_toolbar_copy_cb(self, button):
        buffer = self.textview.get_buffer()
        begin, end = buffer.get_selection_bounds()
        copy_text = buffer.get_text(begin, end)
        self.clipboard.set_text(copy_text)

    def keypress_cb(self, widget, event):
        "Respond when the user presses one of the arrow keys"
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == 'plus':
            self.font_increase()
            return True
        if keyname == 'minus':
            self.font_decrease()
            return True
        if keyname == 'KP_Right':
            self.scroll_down()
            return True
        if keyname == 'Page_Up':
            self.page_previous()
            return True
        if keyname == 'KP_Left':
            self.scroll_up()
            return True
        if keyname == 'Page_Down' :
            self.page_next()
            return True
        if keyname == 'Up'or keyname == 'KP_Up':
            self.scroll_up()
            return True
        if keyname == 'Down' or keyname == 'KP_Down':
            self.scroll_down()
            return True
        return False
        
    def page_next(self):
        page = self.page
        page = page + 1
        if page >= len(self.page_index): page=len(self.page_index) - 1
        self.show_page(page)
        v_adjustment = self.scrolled.get_vadjustment()
        v_adjustment.value = v_adjustment.lower
        self._read_toolbar.set_current_page(page)
        self.page = page

    def page_previous(self):
        page = self.page
        page=page-1
        if page < 0: page=0
        self.show_page(page)
        v_adjustment = self.scrolled.get_vadjustment()
        v_adjustment.value = v_adjustment.upper - v_adjustment.page_size
        self._read_toolbar.set_current_page(page)
        self.page = page

    def font_decrease(self):
        font_size = self.font_desc.get_size() / 1024
        font_size = font_size - 1
        if font_size < 1:
            font_size = 1
        self.font_desc.set_size(font_size * 1024)
        self.textview.modify_font(self.font_desc)

    def font_increase(self):
        font_size = self.font_desc.get_size() / 1024
        font_size = font_size + 1
        self.font_desc.set_size(font_size * 1024)
        self.textview.modify_font(self.font_desc)

    def scroll_down(self):
        v_adjustment = self.scrolled.get_vadjustment()
        if v_adjustment.value == v_adjustment.upper - v_adjustment.page_size:
            self.page_next()
            return
        if v_adjustment.value < v_adjustment.upper - v_adjustment.page_size:
            new_value = v_adjustment.value + v_adjustment.step_increment
            if new_value > v_adjustment.upper - v_adjustment.page_size:
                new_value = v_adjustment.upper - v_adjustment.page_size
            v_adjustment.value = new_value

    def scroll_up(self):
        v_adjustment = self.scrolled.get_vadjustment()
        if v_adjustment.value == v_adjustment.lower:
            self.page_previous()
            return
        if v_adjustment.value > v_adjustment.lower:
            new_value = v_adjustment.value - v_adjustment.step_increment
            if new_value < v_adjustment.lower:
                new_value = v_adjustment.lower
            v_adjustment.value = new_value

    def set_current_page(self, page):
        self.page = page

    def show_page(self, page_number):
        position = self.page_index[page_number]
        self.etext_file.seek(position)
        linecount = 0
        label_text = '\n\n\n'
        while linecount < _PAGE_SIZE:
            line = self.etext_file.readline()
            if not line:
                break
            else:
                label_text = label_text + unicode(line,  "iso-8859-1")
            linecount = linecount + 1
        textbuffer = self.textview.get_buffer()
        label_text = label_text + '\n\n\n'
        textbuffer.set_text(label_text)

    def show_found_page(self, page_tuple):
        position = self.page_index[page_tuple[0]]
        self.etext_file.seek(position)
        linecount = 0
        label_text = '\n\n\n'
        while linecount < _PAGE_SIZE:
            line = self.etext_file.readline()
            if not line:
               break
            else:
                label_text = label_text + unicode(line, "iso-8859-1")
                linecount = linecount + 1
        label_text = label_text + '\n\n\n'
        textbuffer = self.textview.get_buffer()
        tag = textbuffer.create_tag()
        tag.set_property('weight', pango.WEIGHT_BOLD)
        tag.set_property( 'foreground', "white")
        tag.set_property( 'background', "black")
        textbuffer.set_text(label_text)
        iterStart = textbuffer.get_iter_at_offset(page_tuple[1])
        iterEnd = textbuffer.get_iter_at_offset(page_tuple[2])
        textbuffer.apply_tag(tag, iterStart, iterEnd)
        self._edit_toolbar._update_find_buttons()

    def save_extracted_file(self, zipfile, filename):
        "Extract the file to a temp directory for viewing"
        filebytes = zipfile.read(filename)
        f = open("/tmp/" + filename, 'w')
        try:
            f.write(filebytes)
        finally:
            f.close

    def read_file(self, file_path):
        """Load a file from the datastore on activity start"""
        _logger.debug('ReadEtextsActivity.read_file: %s', file_path)
        self._load_document(file_path)

    def write_file(self, filename):
        "Save meta data for the file."
        self.metadata['current_page'] =str(self.page)

    def find_previous(self):
        self.current_found_item = self.current_found_item - 1
        if self.current_found_item <= 0:
            self.current_found_item = 0
        current_found_tuple = self.found_records[self.current_found_item]
        self.page = current_found_tuple[0]
        self._read_toolbar.set_current_page(self.page)
        self.show_found_page(current_found_tuple)

    def find_next(self):
        self.current_found_item = self.current_found_item + 1
        if self.current_found_item >= len(self.found_records):
            self.current_found_item = len(self.found_records) - 1
        current_found_tuple = self.found_records[self.current_found_item]
        self.page = current_found_tuple[0]
        self._read_toolbar.set_current_page(self.page)
        self.show_found_page(current_found_tuple)
    
    def can_find_previous(self):
        if self.current_found_item == 0:
            return False
        return True
    
    def can_find_next(self):
        if self.current_found_item >= len(self.found_records) - 1:
            return False
        return True
    
    def find_begin(self, search_text):
        pagecount = 0
        linecount = 0
        charcount = 0
        self.found_records = []
        self.current_found_item = -1
        self.etext_file.seek(0)
        while self.etext_file:
            line = unicode(self.etext_file.readline(), "iso-8859-1")
            line_length = len(line)
            if not line:
                break
            linecount = linecount + 1
            position = string.find(line, search_text)
            if (position >= 0):
                found_pos = charcount + position + 3
                found_tuple = (pagecount, found_pos, len(search_text) + found_pos)
                self.found_records.append(found_tuple)
                self.current_found_item = 0
            charcount = charcount + line_length  
            if linecount >= _PAGE_SIZE:
                linecount = 0
                charcount = 0
                pagecount = pagecount + 1
        if self.current_found_item == 0:
            current_found_tuple = self.found_records[self.current_found_item]
            self.page = current_found_tuple[0]
            self._read_toolbar.set_current_page(self.page)
            self.show_found_page(current_found_tuple)
    
    def get_current_page(self):
        return self.page

    # The code from here on down is for sharing.
    def _download_result_cb(self, getter, tempfile, suggested_name, tube_id):
        del self.unused_download_tubes

        _logger.debug("Got document %s (%s) from tube %u",
                      tempfile, suggested_name, tube_id)
        self._load_document("file://%s" % tempfile)
        _logger.debug("Saving %s to datastore...", tempfile)
        self.save()

    def _download_progress_cb(self, getter, bytes_downloaded, tube_id):
        # FIXME: signal the expected size somehow, so we can draw a progress
        # bar
        _logger.debug("Downloaded %u bytes from tube %u...",
                      bytes_downloaded, tube_id)

    def _download_error_cb(self, getter, err, tube_id):
        _logger.debug("Error getting document from tube %u: %s",
                      tube_id, err)
        self._want_document = True
        gobject.idle_add(self._get_document)

    def _download_document(self, tube_id):
        # FIXME: should ideally have the CM listen on a Unix socket
        # instead of IPv4 (might be more compatible with Rainbow)
        chan = self._shared_activity.telepathy_tubes_chan
        iface = chan[telepathy.CHANNEL_TYPE_TUBES]
        addr = iface.AcceptStreamTube(tube_id,
                # telepathy.SOCKET_ADDRESS_TYPE_IPV4,
                _SOCKET_TYPE_IPv4,
                # telepathy.SOCKET_ACCESS_CONTROL_LOCALHOST, 0,
                _SOCKET_ACCESS_CONTROL_LOCALHOST, 0,
                utf8_strings=True)
        _logger.debug('Accepted stream tube: listening address is %r', addr)
        # SOCKET_ADDRESS_TYPE_IPV4 is defined to have addresses of type '(sq)'
        assert isinstance(addr, dbus.Struct)
        assert len(addr) == 2
        assert isinstance(addr[0], str)
        assert isinstance(addr[1], (int, long))
        assert addr[1] > 0 and addr[1] < 65536
        port = int(addr[1])

        getter = network.GlibURLDownloader("http://%s:%d/document"
                                           % (addr[0], port))
        getter.connect("finished", self._download_result_cb, tube_id)
        getter.connect("progress", self._download_progress_cb, tube_id)
        getter.connect("error", self._download_error_cb, tube_id)
        _logger.debug("Starting download to %s...", self._jobject.file_path)
        getter.start(self._jobject.file_path)
        return False

    def _get_document(self):
        if not self._want_document:
            return False

        # Assign a file path to download if one doesn't exist yet
        if not self._jobject.file_path:
            self._jobject.file_path = os.path.join(tempfile.gettempdir(), '%i' % time.time())
            self._owns_file = True

        # Pick an arbitrary tube we can try to download the document from
        try:
            tube_id = self.unused_download_tubes.pop()
        except (ValueError, KeyError), e:
            _logger.debug('No tubes to get the document from right now: %s',
                          e)
            return False

        # Avoid trying to download the document multiple times at once
        self._want_document = False
        gobject.idle_add(self._download_document, tube_id)
        return False

    def _joined_cb(self, also_self):
        self.watch_for_tubes()
        gobject.idle_add(self._get_document)

    def _load_document(self, filename):
        "Read the Etext file"
        if filename.endswith(".zip"):
            self.zf = zipfile.ZipFile(filename, 'r')
            self.book_files = self.zf.namelist()
            self.save_extracted_file(self.zf, self.book_files[0])
            current_file_name = "/tmp/" + self.book_files[0]
        else:
            current_file_name = filename
            
        self.etext_file = open(current_file_name,"r")
        
        self.page_index = [ 0 ]
        pagecount = 0
        linecount = 0
        while self.etext_file:
            line = self.etext_file.readline()
            if not line:
                break
            linecount = linecount + 1
            if linecount >= _PAGE_SIZE:
                position = self.etext_file.tell()
                self.page_index.append(position)
                linecount = 0
                pagecount = pagecount + 1
        self.page = int(self.metadata.get('current_page', '0'))
        self.show_page(self.page)
        self._read_toolbar.set_total_pages(pagecount + 1)
        self._read_toolbar.set_current_page(self.page)
        if filename.endswith(".zip"):
            os.remove(current_file_name)

        # We've got the document, so if we're a shared activity, offer it
        if self.get_shared():
            self.watch_for_tubes()
            self._share_document()

    def _share_document(self):
        # FIXME: should ideally have the fileserver listen on a Unix socket
        # instead of IPv4 (might be more compatible with Rainbow)

        # FIXME: there is an issue with the Activity class and Read that makes
        # the pdf file disappear; probably related to write_file not writing a
        # file. This is a dirty fix and should be improved later.
        if self._jobject is None:
            self._jobject = datastore.get(self._object_id)
        elif not os.path.exists(self._jobject.get_file_path()):
            self._jobject.destroy()
            self._jobject = datastore.get(self._object_id)

        self._fileserver = ReadHTTPServer(("", self.port),
            self._jobject.get_file_path())

        # Make a tube for it
        chan = self._shared_activity.telepathy_tubes_chan
        iface = chan[telepathy.CHANNEL_TYPE_TUBES]
        self._fileserver_tube_id = iface.OfferStreamTube(READ_STREAM_SERVICE,
                {},
                # telepathy.SOCKET_ADDRESS_TYPE_IPV4,
                _SOCKET_TYPE_IPv4,
                ('127.0.0.1', dbus.UInt16(self.port)),
                # telepathy.SOCKET_ACCESS_CONTROL_LOCALHOST, 0)
                _SOCKET_ACCESS_CONTROL_LOCALHOST, 0)

    def watch_for_tubes(self):
        tubes_chan = self._shared_activity.telepathy_tubes_chan

        tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal('NewTube',
            self._new_tube_cb)
        tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb,
            error_handler=self._list_tubes_error_cb)

    def _new_tube_cb(self, tube_id, initiator, tube_type, service, params,
                     state):
        _logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
                      'params=%r state=%d', tube_id, initiator, tube_type,
                      service, params, state)
        if service == READ_STREAM_SERVICE:
            _logger.debug('I could download from that tube')
            self.unused_download_tubes.add(tube_id)
            # if no download is in progress, let's fetch the document
            if self._want_document:
                gobject.idle_add(self._get_document)

    def _list_tubes_reply_cb(self, tubes):
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        _logger.error('ListTubes() failed: %s', e)

    def _shared_cb(self, activity):
        # We initiated this activity and have now shared it, so by
        # definition we have the file.
        _logger.debug('Activity became shared')
        self.watch_for_tubes()
        self._share_document()
