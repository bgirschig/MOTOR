# pylint: disable=E0611,E0401

import webapp2
import cloudstorage as gcs
from os.path import basename
from google.appengine.api import app_identity
import os
import jinja2
import urllib
import time
from common.storage_utils import get_signed_url, get_renders

is_dev_appserver = os.environ['APPLICATION_ID'].startswith("dev")
bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
retry_params = gcs.RetryParams(backoff_factor=1.1)

jinja = jinja2.Environment(
	loader=jinja2.FileSystemLoader("gui_templates"),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class ResultsPage(webapp2.RequestHandler):
	def get(self, request_id):
		files = [{
			"name": basename(item.filename),
			"href": get_signed_url(item.filename),
		} for item in get_renders(request_id)]
		
		html = jinja.get_template('render_result.html').render({
			"files": files,
		})

		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(html)