# pylint: disable=E0611,E0401

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import logging
import mailParser
import html_parser
from time import time
from common.task_queue_client import Queue
from mailRenderer import create_mail

TASK_QUEUE_API_URL = 'https://task-queue-dot-kairos-motor.appspot.com'
queue = Queue()

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