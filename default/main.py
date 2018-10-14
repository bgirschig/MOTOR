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
from task_queue_client import Queue

SELF_EMAIL = "render@kairos-motor.appspotmail.com"
ACCEPT_STATUS_CODES = [200, 201, 202]
RENDERER_API_URL = 'http://40.89.131.172:8081/render'
# RENDERER_API_URL = 'http://localhost:8081/render'
TEMPLATES_PATH = path.join(path.dirname(__file__), 'scrapers')
TASK_QUEUE_API_URL = 'http://localhost:8082'

# TODO: use cloud endpoints for managing user limits, monitoring, etc...
# TODO: move render nodes to gcloud compute engine

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_PATH),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

queue = Queue(TASK_QUEUE_API_URL)

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
            
            # determine request id
            string_req = json.dumps(request_datas) + str(randrange(0, 10**14))
            request_datas['id'] = hashlib.md5(string_req).hexdigest()
            
            # append other request informations
            request_datas["clientID"] = mail_message.sender
            request_datas["requesterID"] = mail_message.sender
            request_datas["timestamp"] = time()

            requests.append(request_datas)

        # print json.dumps(requests, indent=2)
        # return

        # Send recap email: parsed info, parsing errors, etc...
        send_recap_mail(requests, mail_message.sender)
        
        for request in requests:
            send_request(request)

        logging.info('[main handler] done')

def send_request(request_data):
    # skip 'errored' requests
    if 'error' in request_data: return

    try:
        logging.info({'tag': 'render-request', 'message': 'sending request',
            'request_data': request_data})

        result = urlfetch.fetch(
            url=RENDERER_API_URL,
            method=urlfetch.POST,
            payload=json.dumps(request_data),
            headers={
                'Content-Type': 'application/json'
            }
        )
        if result.status_code not in ACCEPT_STATUS_CODES:
            raise Exception('failed request: [{}] {}'.format(
                result.status_code, result.content))
        
    except Exception as err:
        logging.error({
            'tag': 'render-request',
            'type': type(err).__name__,
            'message': err.message,
            'request_id': request_data['id'],
            'request_data': request_data,
        })

def send_recap_mail(requests, address):
    logging.info('send_recap_mail')
    
    html_template = jinja.get_template('chanel_makeup_mail.html')
    mail_content_html = html_template.render({'requests': requests})
    
    text_template = jinja.get_template('chanel_makeup_mail.txt')
    mail_content_text = text_template.render({'requests': requests})

    message = mail.EmailMessage(
        sender=SELF_EMAIL,
        to=address,
        subject='Your render request',
    )
    message.html = mail_content_html
    message.body = mail_content_text

    message.send()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/queue-test', QueueTest),
    MailRequestHandler.mapping(),
], debug=True)