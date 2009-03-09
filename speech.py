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

import logging

logger = logging.getLogger('readetexts')

supported = True
done = True

try:
    import gst
    gst.element_factory_make('espeak')
    from speech_gst import *
    logger.info('use gst-plugins-espeak')
except:
    try:
        from speech_dispatcher import *
        logger.info('use speech-dispatcher')
    except Exception, e:
        supported = False
        logger.info('disable speech: %s' % e)

voice = None
pitch = PITCH_DEFAULT
rate = RATE_DEFAULT

