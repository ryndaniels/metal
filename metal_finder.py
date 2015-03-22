#!/usr/bin/env python

import sys
import requests
import lxml.html
from bs4 import BeautifulSoup
from sets import Set


def find_links_in_page(page, phrase=None):
	# Returns a list of URLs, if a given phrase is in the link text.
	# If no phrase is given, just return all the links.
	links = []
	for link in BeautifulSoup(page.text).find_all('a'):
		try:
			href = str(link.get('href'))
			if phrase:
				if phrase in str(link.get('title')):
					links.append("http://en.wikipedia.org{}".format(link.get('href')))
			elif not is_link_special(href):
				links.append("http://en.wikipedia.org{}".format(link.get('href')))
		except:
			# No, fuck you, unicode errors
			pass
	return links

def is_link_special(href):
	# Finds out if a link goes to one of the bajillion "special" pages. This method is still pretty janky.
	return "Portal:" in href or "#cite" in href or "/wiki" not in href or "Special:" in href \
	or "Help:" in href or "Category:" in href or "Wikipedia:" in href or "wikimediafoundation" in href \
	or "wikipedia.org" in href or "wikidata.org" in href

def is_actually_band_page(band_url):
	page = lxml.html.parse(band_url)
	if "band" in page.find(".//title").text.lower():
		# this is a pretty good indicator
		return True
	else:
		# Ugh, let's do some shitty analysis on the page
		for body in page.iter('body'):
			if "band" in body.text_content().lower() and "members" in body.text_content().lower() and "years active" in body.text_content().lower():
				return True
	return False


def is_instrument_in_band(band_page, instrument):
	# This is really super naive, but better now that is_actually_band_page() kind of exists.
	# For very generous definitions of better.
	return instrument in band_page.text.lower()

def find_band_genre(band):
	pass

def get_google_play_store_url(band):
	pass

def main():
	bands = Set()

  	if len(sys.argv) != 2:
  		print "Usage: ./metal_finder.py <instrument name>"
		sys.exit(2)

	instrument = sys.argv[1]

	metal_lists_url = "http://en.wikipedia.org/wiki/Category:Lists_of_heavy_metal_bands"
	metal_lists_page = requests.get(metal_lists_url)
	metal_list_links = find_links_in_page(metal_lists_page, "List of") # Only get the links that actually go to lists

	for link in metal_list_links:
		list_page = requests.get(link)
		metal_band_links = find_links_in_page(list_page)

		for band_url in metal_band_links:
			try:
				if is_actually_band_page(band_url):
					band_page = requests.get(band_url)
					if is_instrument_in_band(band_page, instrument):
						bands.add(band_url)
			except Exception as e:
				# Sometimes there's errors. We're too metal to care, just fucking keep going.
				print e
				pass

	if len(bands) > 0:
		print "I found you some metal bands with {}s in!".format(instrument)
		print "\n".join(bands)
	else:
		print "Shocking, no metal bands have {}s in them. Maybe you should start one.".format(instrument)

if __name__ == "__main__":
	main()
