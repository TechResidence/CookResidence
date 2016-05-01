"""`main` is the top level module for your Flask application."""

# -*- coding: utf-8 -*-
from secret import *

import logging
import json
from google.appengine.ext import vendor
vendor.add('lib')
from google.appengine.api import urlfetch

# Import the Flask Framework
from flask import Flask
from flask import request
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

import urllib
import urlparse
import re
import random
from bs4 import BeautifulSoup

@app.route('/')
def hello():
    return 'Hello World!!'

@app.route('/callback', methods=["POST"])
def linebot():
	args = json.loads(request.get_data()) # .decode('utf-8'))
	logging.debug('kick from line server,\n %s'%(args['result']))
	for msg in args['result']:
		tgt_id = msg["content"]["from"]

		# reply anyway
		please_wait(tgt_id)

		# then search recipe
		word = msg["content"]["text"]
		urls = search_in_cookpad(word)
		pairs = [ (get_title(url), url, get_imgurl(url)) for url in random.sample(urls, 3) ]
		print(pairs)

		# answer
		for pair in pairs:
			kickBot(tgt_id , msg["eventType"],  pair)
	return "{}"

@app.route('/facebook')
def facebook():
    return 'facebook'

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

def search_in_cookpad(word):
	# keyword = unicode(word, errors='ignore')
	keyword = urllib.quote(word.encode('utf-8'))
	searchurl = urlparse.urljoin("http://cookpad.com/search/", keyword)
	sock = urllib.urlopen(searchurl)
	htmlSource = sock.read()
	sock.close()
	urls = re.findall(r'http://cookpad.com/recipe/\d+', htmlSource)
	return urls

def create_header_line():
	return {
		'Content-type':'application/json; charset=UTF-8',
		'X-Line-ChannelID':YOURID,
		'X-Line-ChannelSecret':YOURSECRET,
		'X-Line-Trusted-User-With-ACL':YOURACL
	}

def fetch_line(form_fields):
	logging.debug(form_fields)
	url = "https://trialbot-api.line.me/v1/events"
	return urlfetch.fetch(
		url = url,
		payload = json.dumps(form_fields,ensure_ascii=False),
		method = urlfetch.POST,
		headers = create_header_line())

def logging_result(result):
	if result.status_code == 200:
		print('OK: 200')
		logging.debug(result.content)
	else:
		print('NG: not 200')
		logging.debug(result.content)

def please_wait(tgt_id):
	comments = [
		'ちょっとまつクマ',
		'わかった！しらべるクマ',
		'おいしいレシピみつけてくるクマ',
		'クマりんちょ！',
		'おっけークマ'
	]
	form_fields = {
		"to": [str(tgt_id)],
		"toChannel": 1383378250,
		"eventType": 138311608800106203,
		"content": {
			"contentType":1,
			"toType":1,
			"text":"%s"%(random.sample(comments, 1)[0])
		}
	}
	result = fetch_line(form_fields)
	logging_result(result)

def kickBot(tgt_id, event_type, pair):
	title = pair[0]
	recipe_url = pair[1]
	imgurl = pair[2]
	form_fields = {
		"to": [str(tgt_id)],
		"toChannel": 1383378250,
		"eventType": 140177271400161403,
		"content": {
			"messages": [
				{
					"contentType":1,
					"text":u"%s %s"%(title, recipe_url)
				},
				{
					"contentType":2,
					"originalContentUrl":imgurl,
					"previewImageUrl":imgurl
				}
			]
		}
	}
	# form_data = urllib.urlencode(form_fields)
	result = fetch_line(form_fields)
	logging_result(result)

def get_title(url):
	sock = urllib.urlopen(url)
	html = sock.read()
	sock.close()
	s = html.index('title>') + 6
	e = html.index('</title')
	title = html[s:e].decode('utf-8')
	if title.index('by') > 0:
		title = title[:title.index(' by')]
	return title[:30]

def get_imgurl(url):
	sock = urllib.urlopen(url)
	html = sock.read()
	sock.close()
	html = urllib.urlopen(url).read()
	soup = BeautifulSoup(html, 'html.parser')
	imgurl = soup.find(id='recipe-main').find('img').get('src').split('?')[0]
	return imgurl
