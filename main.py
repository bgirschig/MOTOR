import logging
import mailParser
import productParser
from MotorRequest import MotorRequest

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail

import webapp2
import jinja2
import os
from os import path

SELF_EMAIL = "render@kairos-motor.appspotmail.com"
TEMPLATES_PATH = path.join(path.dirname(__file__), 'templates')

# TODO: use cloud endpoints for managing user limits, monitoring, etc...
# TODO: move render nodes to gcloud compute engine

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_PATH),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello world')

class MailRequestHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info(
            'Received a message:\n' + mailParser.stringify(mail_message))

        # Retrieve data from mail text
        data = mailParser.parse(mail_message)
        
        # Scrape found 'requests' for render infos
        items = [productParser.parseItem(item) for item in data['items']]
        
        # create request
        requests = [MotorRequest(mail_message.sender, mail_message.sender, item) for item in items]

        # Send recap email: parsed info, parsing errors, etc...
        send_recap_mail(requests, mail_message.sender)
        
        for request in requests:
            request.send()

def send_recap_mail(requests, address):
    logging.info('send_recap_mail')
    html_template = jinja.get_template('request_confirm_mail.html')
    mail_content_html = html_template.render({'requests': requests})
    text_template = jinja.get_template('request_confirm_mail.txt')
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
    MailRequestHandler.mapping(),
], debug=True)