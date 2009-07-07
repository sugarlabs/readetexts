# Copyright 2009 One Laptop Per Child
# Author: Sayamindu Dasgupta <sayamindu@laptop.org>
#    and James Simmons <nicestep@gmail.com>
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
import time

import gtk

from sugar.graphics.icon import Icon

from gettext import gettext as _

_logger = logging.getLogger('read-activity')

class Sidebar(gtk.EventBox):
    def __init__(self):
        gtk.EventBox.__init__(self)
        self.set_size_request(20, -1)
        # Take care of the background first
        white = gtk.gdk.color_parse("white")
        self.modify_bg(gtk.STATE_NORMAL, white)

        self._box = gtk.VButtonBox()
        self._box.set_layout(gtk.BUTTONBOX_CENTER)
        self.add(self._box)

        self._box.show()
        self.show()

        self.bookmark_icon = Icon(icon_name = 'emblem-favorite', \
            pixel_size = 18)
        tooltip_text = _('Bookmark') 
        self.bookmark_icon.set_tooltip_text(tooltip_text)
        self._box.pack_start(self.bookmark_icon ,expand=False,fill=False)

    def show_bookmark_icon(self, state):
        if state:
            self.bookmark_icon.show_all()
        else:
            self.bookmark_icon.hide()

