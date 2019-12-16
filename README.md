# Laracasts Scraper
Download the entire Laracasts video library with one simple script!

* [Description](#description)
* [Usage](#usage)
* [Requirements](#requirements)
* [Known Issues](#known-issues)

## Description
This is a Python script that was originally written by [Eric Bachhuber](https://gist.github.com/bachhuberdesign/0dfc11cb4a5f959d65dcb914ee7c4dcf) to scrape the Laracasts website and download all of their active (non-archived) videos from each category. It uses the direct download link provided by Laracasts, but they limit the number of videos you can download in a 24 hour window to 30.

I have modified the script to bypass this limitation by instead getting the video directly from the embedded Vimeo source, and to allow the ability to set preferred quality of video download to save bandwidth or download faster.

## Usage
All you have to do is modify the `laravel_session` variable at the top of the script.

If you want, you can also change the `pref_quality` variable as well. Accepted values are `1080` `720` and `360`. Default is `1080`. Do note, some of their videos are not available in 1080. The script will automatically download the next highest quality version.

When you run the script, it will create a folder called Laracasts in the same directory the script file is in. It will organize the files as `Series/Episode # - Episode Name.mp4`. The script will detect if you've already downloaded a file and skip it if you have. This is so you can stop and run the script at a later time and not have to download the entire library again.

**Please note**: If you stop running the script and go to run it at a later time, you will most likely need to update the `laravel_session` variable. You can revisit the laracasts.com website and get the new request header information to get the updated value.

## Requirements
* Active Laracasts Subscription
* Python 3.*
* Modules: requests & beautifulsoup4 - install with pip3

```
Single version of python installed:
    pip install requests
    pip install beautifulsoup4
    
Multiple versions of python installed:
    py -3 -m pip install requests
    py -3 -m pip install beautifulsoup4
```

## Known Issues
* ***Empty or corrupted video files...***

  When attempting to download the video directly from Vimeo's CDNs, the file may sometimes not correctly download and will appear to be a ~269b file.
  
  I have taken a few steps to reduce the frequency of this happening. The script will attempt to download the file up to 3 times, with added pause between downloads. You can modify the `timer` (seconds) variable to increase the amount of time the script waits between downloads. Increasing the time may help reduce incomplete file downloads.

* ***object not subscriptable...***

  If you get a Python error `object not subscriptable`, then it is most likely that the `laravel_session` has expired and will need to be updated. You can revisit the laracasts.com website and get the new request header information to get the updated value.
