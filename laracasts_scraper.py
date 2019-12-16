#--------------------------------------------------
# Laracasts Video Scraper
#
# Original Author: Eric Bachhuber
# Modified by: Devon Elliott
#
# Video files will be saved to a folder called
# "Laracasts" within the directory this script is
# ran from.
#
# Modifications from original script attempt to
# download video from Vimeo CDN source, rather
# than directly from Laracasts to bypass the 30
# video download limit imposed by Laracasts.
#
# Possibly violates the terms of service, so use
# at your own risk.
#
# Required: Active Laracasts Subscription
# Required: Python 3.*
# Required: requests & beautifulsoup4
#           - install with pip3
#--------------------------------------------------
from bs4 import BeautifulSoup
import urllib.request
import json
import requests
import re
import os
import time

# Login to Laracasts via web and paste your laravel_session cookie here (inspect request header to find)
# Must be logged into a Laracasts account with an active subscription
laravel_session = ''

# Set your preferred video quality to download.
# Supported: 1080, 720, 360 - Default 1080
pref_quality = 1080

# Amount of time after each download to pause script.
# This is to help mitigate downloading corrupted video files.
# Default is 5, but still results in some incomplete files.
timer = 5

# ----------------------------------------
# Please don't modify anything below here,
# unless you know what you are doing.
# ----------------------------------------

# Set headers and cookies for requests.
headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36' }
cookies = { 'laravel_session': laravel_session }

def main():
	with requests.Session() as session:
		session.headers = headers

		# Get list of all categories with series via API (auth not required for this API call)
		# Only non-archived series are returned from this endpoint.
		# As of 10/9/2019, there are 79 "current" series and 19 "archived" series
		seriesJson = requests.get('https://laracasts.com/api/series').json()

		for category in seriesJson:
			# As of 10/9/2019, Laracasts has 5 categories:
			# Laravel, PHP, Testing, JavaScript, and Tooling
			print("\nDownloading category: " + category)

			for series in seriesJson[category]:
				seriesTitle = sanitize_for_file_name(series['title'])
				slug = series['slug']

				print("\nPreparing to download series: " + seriesTitle)

				episodeCounter = 1
				while True:
					url = "https://laracasts.com/series/" + slug + "/episodes/" + str(episodeCounter)

					episodeRequest = session.get(
						url,
						headers=headers,
						cookies=cookies,
						allow_redirects=False # prevent redirect to landing page if episode doesn't exist
					)

					# No additional episodes for this series, continue to next series.
					if episodeRequest.status_code == 302:
						break

					# Grab episode data from the page.
					soup = BeautifulSoup(episodeRequest.content, 'html.parser')
					episodeName = sanitize_for_file_name(soup.title.string.replace(seriesTitle, ''))
					episodePath = 'Laracasts/' + seriesTitle + "/Episode " + str(episodeCounter) + " - " + episodeName + ".mp4"

					# Create the directories if they do not exist.
					if not os.path.isdir('Laracasts'):
						os.mkdir('Laracasts')
					if not os.path.isdir('Laracasts/' + seriesTitle):
						os.mkdir('Laracasts/' + seriesTitle)

					# Video file does not exist, lets download it.
					if not os.path.exists(episodePath):
						print("Downloading episode " + str(episodeCounter) + ": " + episodeName + "...")

						download_video(session, url, soup, episodePath)

					# Video file exists, lets double check it then skip if okay.
					else:
						size = os.path.getsize(episodePath)

						if size < 500:
							print("Episode " + str(episodeCounter) + " exists, but is incomplete. Redownloading...")
							download_video(session, url, soup, episodePath)
						else:
							print('Episode ' + episodeName + ' already exists, skipping.')

					# iterate to the next episode
					episodeCounter = episodeCounter + 1
					pass

def sanitize_for_file_name(toSanitize):
	remove_punctuation_map = dict((ord(char), None) for char in '\\/*?:"<>|\'')
	return toSanitize.translate(remove_punctuation_map).strip()

def download_video(session, url, souped, episodePath):
	# Attempt download of video up to 3 times before skipping.
	i = 0
	while i < 3:
		i = i + 1

		# Get the embedded video iframe src.
		video = souped.find('video-player')
		video_url = "https://player.vimeo.com/video/" + video['vimeo-id'] + "?speed=1&color=00b1b3&autoplay=1&app_id=122963"

		# Get information from Vimeo video src page.
		videoRequest = session.get(
			video_url,
			headers={
				'Referer': url
			},
			cookies=cookies,
		)

		soup = BeautifulSoup(videoRequest.content, 'html.parser')
		scripts = soup.body.find_all('script')

		#  Find the direct download link in all qualities from Vimeo CDNs.
		data = soup.find_all("script")[2].text
		config = re.search(r"var config = (.*?);", data)
		config = json.loads(config.group(1))

		q1080 = q720 = q360 = None

		for video in config["request"]["files"]["progressive"]:
			if video["quality"] == "1080p":
				q1080 = video["url"]
			if video["quality"] == "720p":
				q720 = video["url"]
			if video["quality"] == "360p":
				q360 = video["url"]

		if q1080 and pref_quality == 1080:
			videoQuality = "1080p"
			downloadLink = q1080
		elif q720 and pref_quality >= 720:
			videoQuality = "720p"
			downloadLink = q720
		else:
			videoQuality = "360p"
			downloadLink = q360

		downloadRequest = session.get(
			downloadLink,
			headers={
				'Referer': url
			},
			cookies=cookies,
		)

		# Save the video.
		open(episodePath, 'wb').write(downloadRequest.content)

		# Now lets make sure it's a complete video file.
		size = os.path.getsize(episodePath)

		if size < 500:
			if i == 1:
				print("--- Video did not download correctly. Retrying...")

			if i < 3:
				print("--- Retry attempt " + str(i) + " failed. Retrying...")
				time.sleep(timer)
				pass
			else: 
				print("--- Failed downloading video. Moving on...")
				break
		else:
			print("--- Video downloaded! Waiting " + str(timer) + " seconds...")
			break

	# Need to sleep script for a few seconds so next download doesn't mess up.
	time.sleep(timer)

if __name__ == "__main__":
	main()
