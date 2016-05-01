#!/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import json
import requests

verify_token = 'XXXX'
token = 'XXX'

def getCookpadLinks(keyword, link_count=3):
    searchurl=urljoin("http://cookpad.com/search/", keyword)
    sock=urllib.urlopen(searchurl)
    htmlSource=sock.read()
    sock.close()
    links=re.findall(r'http://cookpad.com/recipe/\d+', htmlSource)
    message = '\n'.join(links[:link_count])
    return message

def sendTextMessage(sender, text):
  if len(text) <= 0:
      return
  url = 'https://graph.facebook.com/v2.6/me/messages'
  headers = {'content-type': 'application/json'}
  data = {"recipient": {"id":sender},"message": {"text":text}}
  params = {"access_token":token}
  r = requests.post(url, params=params, data=json.dumps(data), headers=headers)

class WebHookHandler(tornado.web.RequestHandler):
    def get(self):
        if self.get_argument("hub.verify_token", "") == verify_token:
            self.write(self.get_argument("hub.challenge", ""))
        else:
            self.write('Error, wrong validation token')
    def post(self):
        print "receive!"
        data = json.loads(self.request.body)
        print data
        messaging_events = data["entry"][0]["messaging"]
        text = ""
        for event in messaging_events:
            sender = event["sender"]["id"]
            if ("message" in event and "text" in event["message"]):
                text = event["message"]["text"]
                sendTextMessage(sender, text)

application = tornado.web.Application([(r"/webhook", WebHookHandler)])

if __name__ == "__main__":
#    application.listen(5000)
#    tornado.ioloop.IOLoop.instance().start()
	pass
