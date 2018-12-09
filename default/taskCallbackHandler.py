# pylint: disable=E0611,E0401

import webapp2
import json
from mailRenderer import create_mail
import logging

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