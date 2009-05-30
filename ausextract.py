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

import getopt
import sys

# This is a script to take the file GUTINDEX.AUS, the offline book catalog of Project Gutenberg Australia, 
# and reformat it for use by Read Etexts.  After the file ausoutput.txt is created it should be combined 
# with the output of gutextract.py and sorted to create bookcatalog.txt.

def main(file_path):

    gut_file = open(file_path,"r")
    out = open("ausoutput.txt", 'w')
    
    while gut_file:
        line = gut_file.readline()
        if not line:
            break
        if len(line) > 78:
            if line[77].isdigit() and line.find("Audio:") < 0 and line[59] == '[':
                path = 'PGA/ebooks' + line[6:8] + '/' + line[60:66] + '1.zip'
                line = line[9:59]
                line = line.rstrip()
                if line.find(', by ') > -1:
                    line = line.replace(', by ', '|')
                else:
                    comma_pos = line.rfind(',')
                    if comma_pos > -1:
                        line = line[0:comma_pos] + '|' + line[comma_pos+1:len(line)].lstrip()
                    else:
                        line = line + '| '
                out.write(line + '|' + path + '\n')
    gut_file.close()
    out.close()
    print "All done!"

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        main(args[0])
    except getopt.error, msg:
        print msg
        print "This program has no options"
        sys.exit(2)
