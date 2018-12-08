# pylint: disable=E0611,E0401

""" renders email, according to jinja templates """

import jinja2
from google.appengine.api import mail
from jinja2.exceptions import TemplateNotFound

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader("mail_templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

SELF_EMAIL = "render@kairos-motor.appspotmail.com"

def create_mail(template_name, data, subject="message", **kwargs):
    # Get mail templates from name. At least one matching template is required
    try:
        text_template = jinja.get_template(template_name+'.txt')
    except TemplateNotFound:
        text_template = None
    try:
        html_template = jinja.get_template(template_name+'.html')
    except TemplateNotFound:
        html_template = None
    if not html_template and not text_template:
        raise TemplateNotFound("no email template "+template_name+" was not found (html or text)")
    
    # create message with default values adn rendered data
    message = mail.EmailMessage(
        sender=SELF_EMAIL,
        html=html_template.render(data) if html_template else "",
        body=text_template.render(data) if text_template else "",
        subject="MOTOR - "+subject
    )

    # override message attributes with values from kwargs
    for key in kwargs:
        setattr(message, key, kwargs[key])

    return message