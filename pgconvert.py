#! /usr/bin/env python3

# Copyright (C) 2010 James D. Simmons
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

LINE_LENGTH = 80
MAX_LINE_LENGTH = 100
MAX_PARAGRAPH_LINES = 25
MAX_LENGTH = (LINE_LENGTH * MAX_PARAGRAPH_LINES)

# This is a script to take the a file in PG format and convert it to a text file readable by Read Etexts that do
# not have newlines at the end of each line.

def convert(file_path,  output_path):

    pg_file = open(file_path,"rb")
    out = open(output_path, 'w')
    previous_line_length = 0
    paragraph_length = 0
    conversion_rejected = False

    while pg_file:
        line = pg_file.readline().decode('iso-8859-1')
        outline = ''
        if not line:
            break
        if len(line) == 2 and not previous_line_length  == 2:
            # Blank line separates paragraphs
            outline = line + '\r\n'
            paragraph_length = 0
        elif len(line) == 2 and previous_line_length == 2:
            outline = line
            paragraph_length = 0
        elif line[0] == ' ' or (line[0] >= '0' and line[0] <= '9'):
            outline = '\r\n' + line[0:len(line)-2] 
            paragraph_length = 0
        else:
            outline = line[0:len(line)-2] + ' '
            paragraph_length = paragraph_length + len(outline)
        out.write(outline)
        previous_line_length = len(line)
        if len(line) > MAX_LINE_LENGTH or paragraph_length > MAX_LENGTH:
            conversion_rejected = True
            break
    pg_file.close()
    out.close()
    print("All done!")
    if conversion_rejected:
        return False
    else:
        return True

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if check(args[0]):
            print('It has NOT been converted yet.')
            success = convert(args[0],  args[1])
            print('Success', success)
        else:
            print('It is ALREADY converted.')
    except getopt.error as msg:
        print(msg)
        print("This program has no options")
        sys.exit(2)
