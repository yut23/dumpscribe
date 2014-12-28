
Download all written notes and recorded audio from a LiveScribe Pulse or Echo pen. Convert the proprietary formats to open formats (pdf and ogg vorbis). Make the notes available online through a web app.

This program has four parts:
 
# dumpscribe

The dumpscribe command downloads and extracts all relevant info from the smartpen in the raw format as it exists on the pen. The audio is in aac format. The written notes are in a proprietary format called stf and the meta-data is in a combination of XML and undocumented binary files.

## Usage

```
./dumpscribe [-d] output_dir

  -d: Enable debug output.
  -c: Delete files from pen after successful download.
```

Where output_dir is a directory where the downloaded data will be saved.

# unmuddle.py

The unmuddle.py command converts written notes to PDF, converts audio data to Ogg Vorbis, parses meta-data and puts everything into a sane folder structure. It can optionally generate PNG thumbnails of the PDFs and combine all pages into a single PDF.

## Usage

```
Usage: unmuddle.py [-h] [--aac] [--notebook] [--thumb] [--thumbsize THUMBSIZE]
                               input_dir output_dir

Convert file formats and organize output from dumpscribe.

positional arguments:
  input_dir             The directory generated by dumpscribe.
  output_dir            Where to write the output from this program.

optional arguments:
  -h, --help            show this help message and exit
  --aac                 Don't convert aac audio files to ogg vorbis.
                        (conversion required either ffmpeg or avconv)
  --notebook            Additionally create one pdf per notebook with all
                        notebook pages (requires pdftk).
  --thumb               Generate png thumbnails of pdfs (requires either
                        ImageMagick or GraphicsMagick).
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
Usage: usb_watcher.py [-h] [-d] [-c POST_COMMAND] dumpscribe_dir dumpscribe_output_dir organized_output_dir [cleanup_dir]

Automatically run dumpscribe when LiveScribe pen is connected.

positional arguments:
  dumpscribe_dir        The full path to the directory where dumpscribe is
                        installed.
  dumpscribe_output_dir
                        Where dumpscribe should place its output.
  organized_output_dir  Where unmuddle should place its output.

  cleanup_dir           Optional directory to clean up if drive is more than
                        50 percent full.

optional arguments:
  -h, --help            show this help message and exit
  -d                    Daemonize this process
  -l                    Enable Beagle Bone Black LED control
  -c POST_COMMAND       Command to run after running unmuddle.py
```

The -l argument only works on a Beagle Bone Black with the Adafruit Beagle Bone BPIO python library installed. If enabled, it will use led_control.py to indicate the current status using three LEDs as output. Modify led_control.py to change which GPIO pins to use and remember that the Beagle Bone Black GPIO pins cannot supply enough current to drive LEDs directly. You'll need to use transistors. 

If cleanup_dir is specified, files are deleted from that directory (by the cleanup.py script) until the usage is under 50% on the device where the directory resides or until there are no more files in the directory. If deleting a file causes a directory to become empty, the empty directory is also deleted.

## Running as a daemon

To run usb_watcher.py as a daemon that automatically starts on boot, first copy the the init script:

```
sudo cp init_scripts/dumpscribe-usb-watcher /etc/init.d/
```

Then make the script start on boot:

```
sudo update-rc.d dumpscribe-usb-watcher defaults
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

Installing requirements for usb_watcher.py:

```
sudo apt-get install python-daemon
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

# Running the web app as a daemon

If you want to run the web app as a daemon, e.g. on a VPS so everyone can access it, then follow the notes in this section.

## Making the web app auto-start 

This section will show how to make the dumpscribe web app auto-start on boot. This method will also make the web app automatically restart if it crashes. 

This section assumes that you have already gotten the dumpscribe web app running on the server by downloading it, installing requirements and editing the config file. See previous sections for instructions. 

This section assumes that dumpscribe is located in /opt/dumpscribe

First check if /usr/bin/node exists:

```
ls /usr/bin/node
```

If it doesn't, make a symlink (otherwise the upstart script won't run):

```
cd /usr/bin
sudo ln -s nodejs node
```

Install "forever" (a node.js app that automatically auto-starts your process when it crashes):

```
sudo npm -g install forever
```

Add a user that will be running dumpscribe (just hit enter when asked questions):

```
sudo adduser dumpscribe --disabled-password
```

Make the dumpscribe dir owned by the dumpscribe user:

```
sudo chown -R dumpscribe.dumpscribe /opt/dumpscribe
```

Now copy the web app's upstart script:

```
sudo cp init_script/dumpscribe-web.conf /etc/init
```

Then, edit /etc/init/dumpscribe-web.conf setting the following lines to the correct values for your system:

```
env APPLICATION_WORKDIR="/opt/dumpscribe/web" # where the web app is located
env UNMUDDLE_OUTPUT_DIR="/opt/dumpscribe/unmuddled" # where the output from unmuddle.py is located
env PIDFILE="/opt/dumpscribe/dumpscribe.pid" # where to keep the pid file 
env LOG="/opt/dumpscribe/dumpscribe.log" # where to write the log
```

Start the dumpscribe web app with:

```
sudo start dumpscribe-web
```

Check if it's really working by visiting the web app in the browser at http://your-server.org:3000/ or seeing if the dumpscribe process is runnning:

```
ps aux|grep index.js|grep -v grep
```

If the upstart script isn't working, uncomment the lines:

```
# exec 2>>/tmp/dumpscribe.fail.log
# set -x
```

Then to see what's going wrong do:

```
sudo start dumpscribe-web
less /tmp/dumpscribe.fail.log
```

## Using an apache reverse proxy

Having users type a URL ending in :3000 is not very nice (and besides, some corporate firewall will block port 3000). Setting up a reverse proxy is the way to go.

If you haven't already, install a apache2:

```
sudo apt-get install apache2
```

Enable some necessary apache2 modules:

```
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod alias
```

Now edit the file apache virtual hosts file for the host where you want dumpscribe-web to appear. If you just now installed apache2, edit the file /etc/apache2/sites-enabled/000-default.conf. Assuming your hostname is myhostname.org and you want the dumpscribe web app to appear at "http://myhostname.org/labnotes" add the following lines immediately before the </VirtualHost> line:

```
RedirectMatch /labnotes$ http://myhostname.org/labnotes/
ProxyRequests Off 
ProxyPass /labnotes/ http://127.0.0.1:3000/
ProxyPassReverse /labnotes/ http://127.0.0.1:3000/
ProxyPreserveHost on 
```

Note that the trailing slashes are important.

Now restart apache:

```
sudo /etc/init.d/apache2 restart
```

Make sure the dumpscribe web app is running, open the url http://myhostname.org/labnotes in a browser to verify that everything is working.

# TODO

* Add stuff from led_control_remote.py to usb_watcher
* Remove my ssh key from BBB and make BBB autogen new key in /root/.ssh/id_rsa* on first boot
* Get rid of dumpscribe memory leaks
** It looks like the obex downloads allocates memory that is only freed when the obex cleanup function is called (which disconnects).
** Use Valgrind to check for memory leaks: http://www.cprogramming.com/debugging/valgrind.html
* Get rid of dumpscribe compile warnings related to xmlChar vs. char

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
