#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Scrapes backpage México to generate human trafficking leads. """

import datetime
import logging
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as etree
from time import sleep
from bs4 import BeautifulSoup

__author__ = "Mike9fromOuterSpace"
__license__ = "GPL"
__version__ = "0.1"

# Defaults
LOGFILE = "logs/mx-backpage.log"
IMG_PATH = "images/"

# ToDo:
# * Seach by location.
# * Search by category.
# * Generate an ID for each ad.
# * Read URLs that will be scraped from a seed file.
# * Implement non-blocking parsing.

def download_feed(url):
	req = urllib.request.urlopen(url)
	tree = etree.parse(req)
	root = tree.getroot()
	return root

"""
Traverses de XML tree, adding all URL/datetime pairs to a dictionary.
"""
def traverse_tree(tree):
	# ToDo: Use Beautiful Soup for this methid instead of etree.
	last_build_date = tree[0].find("lastBuildDate").text
	# ToDo: Parse last_build_date as datetime object.
	# ToDo: Verify that build date is more recent than the last fetch.
	
	ad_urls = {}
	for child in tree[0].findall("item"):
		pub_date = child.find("pubDate").text
		# ToDo: Parse pubDate as datetime object.
		ad_url = child.find("link").text
		ad_urls[ad_url] = pub_date
	return ad_urls

"""
Scrapes an individual page and fetches: page title, ad title, description, and image URLs.
"""
def scrape_document(ad_url, pub_date):
	req = urllib.request.urlopen(ad_url)
	soup = BeautifulSoup(req, "html.parser")
	
	doc_title = soup.title # The HTML Title
	title = soup.find("a", attrs={"class": "h1link"}).text
	description = soup.find("div", attrs={"class": "postingBody"}).text

	img_tags = soup.find_all("img")
	image_urls = []
	for i in img_tags:
		image_urls.append(i.attrs["src"])

	doc = {}
	doc["doc_title"] = doc_title
	doc["date_published"] = pub_date
	doc["date_fetched"] = datetime.datetime.utcnow()
	doc["title"] = title
	doc["description"] = description
	doc["images"] = image_urls

	time.sleep(0.5)

	return doc

"""
Downloads images from an ad.
"""
# Images filenames in the server do not follow any pattern.
# Images appear to be stored under a numer username.
def fetch_images(ad_id, images):
	for url in images:
		# (?) Should the original filename be kept?
		filename = os.path.join("images", ad_id)
		# Fix this:
		with urllib.request.urlopen(url) as response, open(filename+".jpg", 'wb') as out_file:
			data = response.read()
			out_file.write(data)
	return


def main():
	path = os.path.dirname(os.path.abspath(__file__))
	logfile = os.path.join(path, LOGFILE)
	logging.basicConfig(level=logging.INFO, filename=logfile, format='%(asctime)s %(message)s')
	logging.info("Starting scraper...")

	# ToDo: Load form seeds.
	url = "http://mexico.backpage.mx/online/exports/Rss.xml?category=4161448&section=4381"
	#"http://mexico.backpage.mx/Domination/""
	#"http://mexico.backpage.mx/FemaleEscorts/"
	#"http://mexico.backpage.mx/BodyRubs/"
	#"http://mexico.backpage.mx/Strippers/"
	#"http://mexico.backpage.mx/Domination/"
	#"http://mexico.backpage.mx/TranssexualEscorts/"
	#"http://mexico.backpage.mx/AdultJobs/
	
	# ToDo: Handle exceptions.
	tree = download_feed(url)	
	ads = traverse_tree(tree)
	
	for ad in ads:
		url = ad	
		pub_date = ads[ad]
		doc = scrape_document(url, pub_date)
		# ToDo: Split in a smarter way.
		ad_id = url.split("/")[-1]
		fetch_images(ad_id, doc["images"])

if __name__ == '__main__':
	main()