# mybutton.py  A version of ActivityToolbarButton that hides the "Keep"
# button.

# Copyright (C) 2010  James D. Simmons
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  US
import gtk
import gconf

from sugar.graphics.toolbarbox import ToolbarButton
from sugar.activity.widgets import ActivityToolbar
from sugar.graphics.xocolor import XoColor
from sugar.graphics.icon import Icon
from sugar.bundle.activitybundle import ActivityBundle

def _create_activity_icon(metadata):
    if metadata.get('icon-color', ''):
        color = XoColor(metadata['icon-color'])
    else:
        client = gconf.client_get_default()
        color = XoColor(client.get_string('/desktop/sugar/user/color'))

    from sugar.activity.activity import get_bundle_path
    bundle = ActivityBundle(get_bundle_path())
    icon = Icon(file=bundle.get_icon(), xo_color=color)

    return icon

class MyActivityToolbarButton(ToolbarButton):

    def __init__(self, activity, **kwargs):
        toolbar = ActivityToolbar(activity, orientation_left=True)
        toolbar.stop.hide()
        toolbar.keep.hide()

        ToolbarButton.__init__(self, page=toolbar, **kwargs)

        icon = _create_activity_icon(activity.metadata)
        self.set_icon_widget(icon)
        icon.show()
