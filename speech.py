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

import gtk
import time
import threading

supported = True

try:
    import speechd
except:
    supported = False

done = True

class EspeakThread(threading.Thread):
    def run(self):
        "This is the code that is executed when the start() method is called"
        global done
        self.client = None
        try:
            self.client = speechd.SSIPClient('readetexts')
            self.client._conn.send_command('SET', speechd.Scope.SELF, 'SSML_MODE', "ON")
            if self.speech_voice:
                self.client.set_language(self.speech_voice[1])
                self.client.set_rate(self.speech_rate)
                self.client.set_pitch(self.speech_pitch)
            self.client.speak(self.words_on_page, self.next_word_cb, (speechd.CallbackType.INDEX_MARK,
                        speechd.CallbackType.END))
            done = False
            while not done:
                time.sleep(0.1)
            self.cancel()
            self.client.close()
        except:
            print 'speech-dispatcher client not created'
    
    def set_words_on_page(self, words):
        self.words_on_page = words
        
    def set_activity(self, activity):
        self.activity = activity

    def set_speech_options(self,  speech_voice,  speech_pitch,  speech_rate):
        self.speech_rate = speech_rate
        self.speech_pitch = speech_pitch
        self.speech_voice = speech_voice

    def cancel(self):
        if self.client:
            try:
                self.client.cancel()
            except:
                print 'speech dispatcher cancel failed'
    
    def next_word_cb(self, type, **kargs):
        global done
        if type == speechd.CallbackType.INDEX_MARK:
            mark = kargs['index_mark']
            word_count = int(mark)
            gtk.gdk.threads_enter()
            self.activity.highlight_next_word(word_count)
            gtk.gdk.threads_leave()
        elif type == speechd.CallbackType.END:
            self.activity.reset_current_word()
            done = True
