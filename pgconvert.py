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

import getopt
import sys

# This is a script to take the a file in PG format and convert it to a text file readable by Read Etexts that does
# not have newlines at the end of each line.

# My first attempt to make a pg converter that would remove unneeded  line endings from PG files
# while leaving an already converted file alone didn't work, so plan B is to mark a converted 
# file invisibly by giving it a first line containing four tabs in a row, followed by CR/LF.  If the 
# file has this first line it is already converted, so return False.
def check(file_path):

    rtf_file = open(file_path,"r")
    line = rtf_file.readline()
    rtf_file.close()
    
    if line == '\t\t\t\t\r\n':
        return False
    else:
        return True

def convert(file_path,  output_path):

    pg_file = open(file_path,"r")
    out = open(output_path, 'w')
    out.write('\t\t\t\t\r\n')
    previous_line_length = 0

    while pg_file:
        line = pg_file.readline()
        outline = ''
        if not line:
            break
        if len(line) == 2 and not previous_line_length  == 2:
            # Blank line separates paragraphs
            outline = line + '\r\n'
        elif len(line) == 2 and previous_line_length == 2:
            outline = line
        elif line[0] == ' ' or (line[0] >= '0' and line[0] <= '9'):
            outline = '\r\n' + line[0:len(line)-2] 
        else:
            outline = line[0:len(line)-2] + ' '
        out.write(outline)
        previous_line_length = len(line)
    pg_file.close()
    out.close()
    print "All done!"

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if check(args[0]):
            print 'It has NOT been converted yet.'
            convert(args[0],  args[1])
        else:
            print 'It is ALREADY converted.'
    except getopt.error, msg:
        print msg
        print "This program has no options"
        sys.exit(2)
