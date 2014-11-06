#!/usr/bin/env python

import sys
import os
import errno
import re
import datetime
import struct
import xml.etree.ElementTree as ET

from stf2pdf import STF2PDF

time_offset = 1406057005809 # TODO read this from file

# TODO get these from command line arguments
indir = "tmp" 
outdir = "out"

pages = {}

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def pentime_to_unixtime(pentime):
    return (int(pentime) + time_offset) / 1000

def copy_and_convert_stf(page, stf_path, dest):
    mkdir_p(os.path.dirname(dest))
    f = open(stf_path)

    if page['number'] % 2 > 0:
        bgfile = 'right.png'
    else:
        bgfile = 'left.png'
    STF2PDF(f).convert(dest, os.path.join('backgrounds', bgfile))
    
    os.utime(dest, (page['time'], page['time']))
    f.close()

# Parse page metadata from xml into a dict
xml_root = ET.parse(os.path.join(indir, "written_page_list.xml"))
for e in xml_root.findall('.//lsp/page'):
    address = e.attrib.get('pageaddress')
    if not address:
        continue
    pages[address] = {
        'number': int(e.attrib.get('page')),
        'time': pentime_to_unixtime(e.attrib.get('end_time'))
    }

# find stf files
for root, dirs, files in os.walk(os.path.join(indir, "data")):
    path = root.split('/')
#    print files
#    print (len(path) - 1) *'---' , os.path.basename(root)       
    page_address = None
    for el in path:
        res = re.match("\d+\.\d+\.\d+\.\d+", el)
        if res:
          page_address = res.group(0)

    for file in files:
        res = re.match(".*\.stf$", file)
        if not res or not page_address:
            continue

        page = pages[page_address]

        time = datetime.datetime.fromtimestamp(page['time'])
        timestr = time.strftime('%Y-%m-%d-%H:%M')
        outfile = os.path.join(outdir, 'pages', page_address + '-' + timestr + '.pdf')
        copy_and_convert_stf(page, os.path.join(root, file), outfile)


def copy_audio(audio_file):
    
    info_file = os.path.join(os.path.dirname(audio_file), 'session.info')
    f = open(info_file)
    f.read(16)
    time_raw = f.read(8)
    time = struct.unpack(">Q", time_raw)[0]
    time = pentime_to_unixtime(time)
    f.close()

    # Attempt to get page address of first associated page (if any)
    page_address = None
    pages_file = os.path.join(os.path.dirname(audio_file), 'session.pages')
    try:
        f = open(pages_file, 'rb')
        f.read(6)
        p1_raw = '\x00' + f.read(3)
        p1 = struct.unpack(">I", p1_raw)[0]
        
        p2_raw = f.read(2)
        p2 = struct.unpack(">H", p2_raw)[0]
        
        p3_raw = struct.unpack(">B", f.read(1))[0]
        shared = struct.unpack(">B", f.read(1))[0] # half this byte belongs to p3, half to p4
        p3 = (p3_raw << 4) | (shared >> 4)
        p4_raw = struct.unpack(">B", f.read(1))[0]
        p4 = ((shared & 240) << 8) | p4_raw

        print("address: " + str(p1) + '.' + str(p2) + '.' + str(p3) + '.' + str(p4))
    except:
        pass
#    p3_raw = p3_raw + (shared >> 4)
#    p4_raw = f.read(1)
#    print(type(p3_raw))
#        p2 = struct.unpack(">H", p2_raw)[0]        


#        print "ARRA"
#        pass








# find audio files
for root, dirs, files in os.walk(os.path.join(indir, "userdata")):
    path = root.split('/')
    page_address = None

    audio_id = None
    for el in path:
        res = re.match("[abcdef\d]{16}", el);
        if res:
            audio_id = res.group(0)

    for file in files:
        res = re.match(".*\.aac$", file)
        if not res:
            continue

        print "File: " + res.group(0) + " id: " + (audio_id or "none")
        copy_audio(os.path.join(root, file))