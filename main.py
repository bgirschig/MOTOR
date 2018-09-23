import logging
import mailParser
import productParser
import MotorRequest

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail

import webapp2
import jinja2
import os
from os import path

SELF_EMAIL = "render@kairos-motor.appspotmail.com"
TEMPLATES_PATH = path.join(path.dirname(__file__), 'templates')

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
        productInfos = [productParser.parseItem(item) for item in data['items']]
        
        # Send recap email: parsed info, parsing errors, etc...
        send_recap_mail(productInfos, mail_message.sender)

        # create request
        request = MotorRequest('none', mail_message.sender, {})

        # send request
        # request.send()

def send_recap_mail(data, address):
    template = jinja.get_template('request_confirm_mail.html')
    mailContent = template.render({'products': data})

    mail.send_mail(
        sender=SELF_EMAIL,
        to=address,
        subject='Your render request',
        body=mailContent,
    )

app = webapp2.WSGIApplication([
    ('/', MainPage),
    MailRequestHandler.mapping(),
], debug=True)