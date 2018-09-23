import re
import logging

def parse(mail_message):
    # Is mail valid ? (object, key(?), date not too old, etc...)
    #
    
    # Who is the client / client id
    

    # extract full body
    full_body = ''
    for _encoding, body in mail_message.bodies('text/plain'):
        full_body += body.decode()

    # Extract requested urls
    regex = r"https?:\/\/www\.[\w.]+(?:\/(?:[\w-]+))+\/?"
    matches = re.findall(regex, full_body);

    # additional info ?
    #

    return matches

def stringify(mail_message):
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