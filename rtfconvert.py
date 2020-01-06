#! /usr/bin/env python3

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

# This is a script to take the a file in RTF format and convert it to a text file readable by Read Etexts.

def check(file_path):

    rtf_file = open(file_path,"r")
    line = rtf_file.readline()
    rtf_file.close()
    
    if line.startswith('{\\rtf1'):
        return True
    else:
        return False

def convert(file_path,  output_path):

    rtf_file = open(file_path,"r")
    out = open(output_path, 'w')
    out.write('\t\t\t\t\r\n')
    brace_count = 0

    while rtf_file:
        line = rtf_file.readline()
        if not line:
            break
        line = line.replace('\\s1', '\n')
        line = line.replace('\\s2', '\n')
        line = line.replace('\\pard', '\n')
        line = line.replace('\\par', '\n')
        line = line.replace(' \\i0', '*')
        line = line.replace('\\i ', '*')
        line = line.replace(' \\b0', '_')
        line = line.replace('\\b ', '_')
        line = line.replace('\\emdash', '--')
        line = line.replace('\\line', '\n')
        line = line.replace('\n ', '\n')
        brace_count = brace_count + count_braces(line)
        line = strip_tags(line)
        if brace_count == 1 and line.find('{') < 0 and line.find('}') < 0:
            out.write(line.lstrip(' '))
    rtf_file.close()
    out.close()
    print("All done!")
    
def strip_tags(string):
    index = 0
    copy = True
    output = ''
    while index < len(string):
        if string[index] == '\\':
            copy = False
        if string[index] == ' ':
            copy = True
        if copy == True:
            output = output + string[index]
        index = index + 1
    return output
    
def count_braces(string):
    index = 0
    count = 0
    while index < len(string):
        if string[index] == '{':
            count = count + 1
        if string[index] == '}':
            count = count - 1
        index = index + 1
    return count

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if check(args[0]):
            print('It is an RTF file')
            convert(args[0],  args[1])
        else:
            print('It is NOT an RTF file')
    except getopt.error as msg:
        print(msg)
        print("This program has no options")
        sys.exit(2)
