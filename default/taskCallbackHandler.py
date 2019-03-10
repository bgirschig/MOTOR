# pylint: disable=E0611,E0401

import webapp2
import json
from mailRenderer import create_mail
from google.appengine.api.mail import Attachment
from common.storage_utils import get_renders
import cloudstorage as gcs
import logging
from os.path import basename

class TaskCallbackHandler(webapp2.RequestHandler):
	def post(self):
		data = json.loads(self.request.body)
		if "render" in data["tags"]: renderCallback(data)

		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write('ok')

def renderCallback(data):
	status = data["status"]
	clientMail = data["payload"]["clientID"]
	
	if not clientMail: return
	
	if status == "DONE":
		# create email attachments with the rendered videos
		renders = get_renders(data["key"])
		attachments = [Attachment(basename(item.filename), gcs.open(item.filename).read()) for item in renders]
		# create message
		message = create_mail("success", data, to=clientMail, subject="your render request", attachments=attachments)
		message.send()
	elif status == "FAILED":
		logging.error("failed task "+data["key"])
		message = create_mail("fail", data, to=clientMail, subject="your render request")
		message.send()
	else:
		logging.error("render callback called on non-finished task")
