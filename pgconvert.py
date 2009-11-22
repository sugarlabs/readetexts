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

def convert(file_path,  output_path):

    pg_file = open(file_path,"r")
    out = open(output_path, 'w')
    previous_line_length = 0

    while pg_file:
        line = pg_file.readline()
        outline = ''
        if not line:
            break
        # print line
        if len(line) == 2 and not previous_line_length  == 2:
            # Blank line separates paragraphs
            outline = line + '\r\n'
            # print 'first blank line'''
        elif len(line) == 2 and previous_line_length == 2:
            outline = line
            # print 'multiple blank lines'
        elif line[0] == ' ' or (line[0] >= '0' and line[0] <= '9'):
            outline = '\r\n' + line[0:len(line)-2] 
            # print 'non-wrapped line;'
        else:
            outline = line[0:len(line)-2] + ' '
            # print 'wrapped line'
        out.write(outline)
        previous_line_length = len(line)
    pg_file.close()
    out.close()
    print "All done!"

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        convert(args[0],  args[1])
    except getopt.error, msg:
        print msg
        print "This program has no options"
        sys.exit(2)
