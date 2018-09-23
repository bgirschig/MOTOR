import logging
import mailParser
import productParser

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import mail

import webapp2
import jinja2
import os

SELF_EMAIL = "render@kairos-motor.appspotmail.com"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        mail.send_mail(sender=SELF_EMAIL,
        to='bastien.girschig@gmail.com',
        subject='Your render request',
        body='mailContent')

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello. mail sent')

class MailRequestHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info(
            'Received a message:\n' + mailParser.stringify(mail_message))

        urls = mailParser.parse(mail_message)
        renderRequestHandler(urls)

def renderRequestHandler(urls):
    productInfos = [productParser.parseUrl(url) for url in urls]
    send_recap_mail(productInfos, 'bastien.girschig@gmail.com')

def send_recap_mail(data, address):
    template = JINJA_ENVIRONMENT.get_template('templates/request_confirm_mail.html')
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