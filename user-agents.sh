#! /bin/bash

# wget http://myip.ms/downloads/web_bots/Known_Web_Bots_Web_Bots_2013_Web_Spider_List.zip

tail -n +12 myip.ms-webcrawlers.txt | grep -e "^#" | cut -d" " -f5- > bots.txt
echo Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98) >> bots.txt
