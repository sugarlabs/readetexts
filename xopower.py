#! /usr/bin/env python

# Copyright (C) 2009 James D. Simmons
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
import dbus
import gobject

_HARDWARE_MANAGER_INTERFACE = 'org.laptop.HardwareManager'
_HARDWARE_MANAGER_SERVICE = 'org.laptop.HardwareManager'
_HARDWARE_MANAGER_OBJECT_PATH = '/org/laptop/HardwareManager'

_logger = logging.getLogger('read-etexts-activity')

# start with sleep off
sleep_inhibit = True
service_activated = False
_idle_timer = 0
_service = None

def setup_idle_timeout():
    # Set up for idle suspend
    global _service
    global service_activated
        
    fname = os.path.join('/etc', 'inhibit-ebook-sleep')
    if not os.path.exists(fname):
        try:
            bus = dbus.SystemBus()
            proxy = bus.get_object(_HARDWARE_MANAGER_SERVICE,
                                   _HARDWARE_MANAGER_OBJECT_PATH)
            _service = dbus.Interface(proxy, _HARDWARE_MANAGER_INTERFACE)
            service_activated = True
            logging.debug('Suspend on idle enabled')
        except dbus.DBusException, e:
            _logger.info('Hardware manager service not found, no idle suspend.')
    else:
        logging.debug('Suspend on idle disabled')

def turn_on_sleep_timer():
    global sleep_inhibit
    sleep_inhibit = False
    reset_sleep_timer()

def turn_off_sleep_timer():
    global sleep_inhibit
    sleep_inhibit = True

def reset_sleep_timer():
    global _idle_timer
    if _idle_timer > 0:
        gobject.source_remove(_idle_timer)
    _idle_timer = gobject.timeout_add(5000, _suspend)

def _suspend():
    # If the machine has been idle for 5 seconds, suspend
    global _idle_timer
    global _service
    _idle_timer = 0
    if not sleep_inhibit and _service is not None:
        _service.set_kernel_suspend()

