
Downloads all written notes and recorded audio from a LiveScribe Pulse or Echo pen.

This program has four parts:
 
# dumpscribe

The dumpscribe command downloads and extracts all relevant info from the smartpen in the raw format as it exists on the pen. The audio is in aac format. The written notes are in a proprietary format called stf and the meta-data is in a combination of XML and undocumented binary files.

## Usage

```
./dumpscribe [-d] output_dir

Where output_dir is a directory where the downloaded data will be saved.
The -d flag enables more verbose output which is useful for debugging.
```

# unmuddle.py

The unmuddle.py command converts written notes to PDF, converts audio data to Ogg Vorbis, parses meta-data and puts everything into a sane folder structure. It can optionally generate PNG thumbnails of the PDFs and combine all pages into a single PDF.

## Usage

```
Usage: unmuddle.py [-h] [--aac] [--thumb] [--thumbsize THUMBSIZE]
                               input_dir output_dir

Convert file formats and organize output from dumpscribe.

positional arguments:
  input_dir             The directory generated by dumpscribe.
  output_dir            Where to write the output from this program.

optional arguments:
  -h, --help            show this help message and exit
  --aac                 Don't convert aac audio files to ogg vorbis.
  --thumb               Generate png thumbnails of pdfs.
  --thumbsize THUMBSIZE
                        Set thumbnail maximum dimension.
```

The PDFs generated by the official LiveScribe software use background images to make them look like the actual notebook paper (with lines or grids). After running dumpscribe, you will have two background files for each of the types of notebooks you have written in so far. E.g:

```
dumpscribe_output_dir/userdata/lsac_data/LS_SA0_TUT_P01.png
dumpscribe_output_dir/userdata/lsac_data/LS_SA0_TUT_P02.png
```

To get unmuddle.py to use these backgrounds, make a backgrounds/ directory in the same directory as the unmuddle.py script and copy the pngs like so:

```
backgrounds/left.png
backgrounds/right.png
```

Unfortunately it is not clear how the official livescribe software figures out which backgrounds go with which notebooks, so for now this is manual. If you really need this feature then the best solution is to always use the same type of notebook.

# usb_watcher.py

The usb_watcher.py command waits for a smartpen to be connected to USB and then runs first dumpscribe, then unmuddle.py and optionally a user-supplied command at the end (e.g. to upload the resulting data to a server). It is meant to be run as a daemon.

## Usage

```
Usage: usb_watcher.py [-h] [-d] [-c POST_COMMAND]
                      dumpscribe_dir dumpscribe_output_dir
                      organized_output_dir

Automatically run dumpscribe when LiveScribe pen is connected.

positional arguments:
  dumpscribe_dir        The full path to the directory where dumpscribe is
                        installed.
  dumpscribe_output_dir
                        Where dumpscribe should place its output.
  organized_output_dir  Where unmuddle should place its output.

optional arguments:
  -h, --help            show this help message and exit
  -d                    Daemonize this process
  -c POST_COMMAND       Command to run after running unmuddle.py
```

# dumpscribe-web

A simple node.js web app that lets users browse the written and recorded notes.

# Requirements

Installing requirements for dumpscribe:

```
sudo apt-get install build-essential pkg-config libglib2.0-0 libglib2.0-dev libopenobex1 libopenobex1-dev libusb-1.0-0 libusb-1.0-0-dev libarchive13 libarchive-dev libxml2 libxml2-dev
```

Installing requirements for basic functionality for unmuddle.py:

```
sudo apt-get install python-cairosvg
```

If you want to use thumbnail generation, audio transcoding and generation of per-notebook pdfs, additionally you need:

```
sudo apt-get install graphicsmagick avconv pdftk
```

For usb_watcher.py the following packages are needed:

```
sudo apt-get install python-gobject python-gudev
```

For the web app you need:

```
sudo apt-get install nodejs npm
cd web/
npm install
```

# Compiling

The dumpscribe command is a C program and needs to be compiled. Just run:

```
make
```

# Configuration

The web app needs a settings file. Do:

```
cp web/settings.js.example web/settings.js
```

Then edit the web/settings.js file to at least change the admin password.

# TODO

* Add upstart script
* Make dumpscribe calculate and write timestamp offset to disk when run
** Needs to get the current time from peninfo, calc offset, and write
* Add command line arguments to dumpscribe
* Add support for deleting files from the pen (need to reverse-engineer)
* Get rid of compile warnings related to xmlChar vs. char

# Bugs and limitations

* If two smartpens are connected at once, dumpscribe will segfault.

# License and Copyright

This project is based on, and contains code from, the following projects:

* [libsmartpen](https://github.com/srwalter/libsmartpen)
* [LibreScribe](https://github.com/dylanmtaylor/LibreScribe)

## License

This project is licensed under GPLv2. For more info see the COPYING file.

## Copyright

The code used in dumpscribe and unmuddle.py has had multiple contributors. Not all of them have identified themselves clearly.

* Copyright 2010 to 2011 Steven Walter (https://github.com/srwalter)
* Copyright 2010 Scott Hassan
* Copyright 2011 jhl (?)
* Copyright 2011 Nathanael Noblet (nathanael@gnat.ca)
* Copyright 2011 to 2013 Dylan M. Taylor (webmaster@dylanmtaylor.com)
* Copyright 2013 Yonathan Randolph (yonathan@gmail.com) 
* Copyright 2014 Robert Jordens (https://github.com/jordens)
* Copyright 2014 Ali Neishabouri (ali@neishabouri.net)
* Copyright 2014 Marc Juul (scribedump@juul.io)
