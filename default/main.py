# pylint: disable=E0611,E0401

import logging
import mailParser
import html_parser

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail
from google.appengine.api.modules.modules import get_current_module_name

import webapp2
import jinja2
import os
from os import path
import json
from time import time
import hashlib
from random import randrange
from google.appengine.api import urlfetch
from common.task_queue_client import Queue
from mailRenderer import create_mail

SELF_EMAIL = "render@kairos-motor.appspotmail.com"
TASK_QUEUE_API_URL = 'https://task-queue-dot-kairos-motor.appspot.com'

# TODO: use cloud endpoints for managing user limits, monitoring, etc...
# TODO: move render nodes to gcloud compute engine

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(""),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

queue = Queue()

class MainPage(webapp2.RequestHandler):
    def get(self):
        service_name = get_current_module_name()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(service_name + ' ok')

class QueueTest(webapp2.RequestHandler):
    def get(self):
        tasks = queue.list()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(tasks))

class TaskCallbackHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        status = data["status"]
        clientMail = data["payload"]["clientID"]
        if clientMail:
            if status == "DONE":
                create_mail("success", data, to=clientMail, subject="your render request").send()
            elif status == "FAILED":
                logging.error("failed task "+data["key"])
                create_mail("fail", data, to=clientMail, subject="your render request").send()

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('ok')

class MailRequestHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info(
            'Received a message:\n' + mailParser.stringify(mail_message))

        # Retrieve data from mail text
        maildata = mailParser.parse(mail_message)
        
        # Scrape found 'requests' for render infos
        requests = []
        for mail_request_item in maildata['requests']:
            request_datas = html_parser.scrapeUrl(
                mail_request_item['url'], './scrapers/chanel_makeup.json')
            
            # append other request informations
            request_datas["clientID"] = mail_message.sender
            request_datas["requesterID"] = mail_message.sender
            request_datas["timestamp"] = time()

            requests.append(request_datas)
        
        for request in requests:
            key = queue.appendTask(request, ["render"], 4)["task_key"]
            request["id"] = key

        # Send recap email: parsed info, parsing errors, etc...
        create_mail('chanel_makeup', {"requests":requests},
            to=mail_message.sender, subject='Your render request').send()

        logging.info('[main handler] done')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/queue-test', QueueTest),
    ('/task_callback', TaskCallbackHandler),
    MailRequestHandler.mapping(),
], debug=True)