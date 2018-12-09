# pylint: disable=E0611,E0401

import webapp2
import cloudstorage as gcs
from os import path
from google.appengine.api import app_identity
import os
import jinja2
import urllib
import time
from base64 import b64encode

is_dev_appserver = os.environ['APPLICATION_ID'].startswith("dev")
bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
retry_params = gcs.RetryParams(backoff_factor=1.1)

jinja = jinja2.Environment(
	loader=jinja2.FileSystemLoader("gui_templates"),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

if is_dev_appserver:
	folder_path = "/" + bucket_name + "/render_outputs/qwertyuiop/"
	with gcs.open(folder_path+"test_1", "w", retry_params=retry_params) as f:
		f.write("hi there")
	with gcs.open(folder_path+"test_2", "w", retry_params=retry_params) as f:
		f.write("hi there 2")

class ResultsPage(webapp2.RequestHandler):
	def get(self, request_id):
		base_path = "/"+bucket_name+"/render_outputs/"
		folder_path = base_path+request_id+"/"
		file_list = gcs.listbucket(folder_path, retry_params=retry_params)
		files = [{
			"name": item.filename.replace(folder_path, ""),
			"href": get_signed_url(item.filename),
		} for item in file_list]
		
		html = jinja.get_template('render_result.html').render({
			"files": files,
		})

		self.response.headers['Content-Type'] = 'text/html'
		self.response.write(html)

def get_signed_url(resource, delay=3600):
    """Return a signed URL for Google Cloud Storage access
    args:
        resource: ressource to get the url for
    kwargs:
        delay: time in seconds from now for which link is valid
    """
    method = "GET"
    content_md5 = ""
    content_type = ""
    expires = str(int(time.time()) + delay)
 
    blob = "\n".join([method, content_md5, content_type, expires, resource])
    _signing_key_name, signature = app_identity.sign_blob(blob)
    signature = b64encode(signature)
    signature = signature.replace(r"+", r"%2B").replace(r"/", r"%2F")
    
    url = "https://storage.googleapis.com{}?GoogleAccessId={}&Expires={}&Signature={}".format(
      resource,
			app_identity.get_service_account_name(),
			expires,
			signature
		)

    return url