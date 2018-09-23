import re
import logging
from datetime import datetime
from datetime import date

def pre_validate(mail_message):
    """Validations that can be performed before parsing mail body (eg. email is
    valid, message is not too old, etc...)
    
    Arguments:
        mail_message {MailMessage} -- The mail message, as received by the InboundMailHandler
    """

    # TODO: Implement this. Throw errors when not valid

    # message age
    # date_reg = r"\w{2,4},\s(\d{2})\s(\w{2,4})\s(\d{4})\s(\d{2}):(\d{2}):(\d{2})"
    
    # sender is an authorized email
    # Note: one client should be able to register multiple emails as authorized

def parse(mail_message):
    """parses email body for render requests
    
    Arguments:
        mail_message {MailMessage} -- The mail message, as received by the InboundMailHandler
    
    Returns:
        Dictionnary -- The parsed data
    """

    pre_validate(mail_message)

    # extract full body
    full_body = ''
    for _encoding, body in mail_message.bodies('text/plain'):
        full_body += body.decode()

    # Extract requested urls
    url_regex = r"https?:\/\/www\.[\w.]+(?:\/(?:[\w-]+))+\/?"
    found_urls = re.findall(url_regex, full_body)
    found_urls = set(found_urls)

    # We return this object, instead of a simple list of urls because the parsed
    # data may include other information in the future. For instance, this
    # allows for adding global settings, or per-item settings without
    # refactoring anything
    return {
        'items': [
            {'url': found_urls}
        ]
    }

def stringify(mail_message):
    """returns a human-readable string representing the given mail_message
    
    Arguments:
        mail_message {MailMessage} -- the message to be stringified
    
    Returns:
        string -- the stringified message
    """

    output = '\n'.join([
        'sender: ' + (mail_message.sender if hasattr(mail_message, 'sender') else '--not defined--'),
        'subject: ' + (mail_message.subject if hasattr(mail_message, 'subject') else '--not defined--'),
        'to: ' + (mail_message.to if hasattr(mail_message, 'to') else '--not defined--'),
        'date: ' + (mail_message.date if hasattr(mail_message, 'date') else '--not defined--'),
    ])
    output += '\n-------------------- body:\n'
    for _encoding, body in mail_message.bodies('text/plain'):
        output += body.decode()
    output += '\n--------------------------'
    return output