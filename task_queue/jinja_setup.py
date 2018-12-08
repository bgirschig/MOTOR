# pylint: disable=E0611,E0401

import datetime
import jinja2

### jinja setup ###
jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


### jinja filters ###

def datetime_filter(timestamp):
  if not timestamp: return "N/A"

  data_format = '%Y-%m-%d %H:%M:%S'
  return datetime.datetime.utcfromtimestamp(timestamp).strftime(data_format)

def timeout_filter(timestamp, status="PENDING"):
  if status is not "RUNNING": return "--"
  if not timestamp: return "N/A"
  
  now = datetime.datetime.now()
  itemTime = datetime.datetime.fromtimestamp(timestamp)
  
  print now, "---", itemTime
  if now > itemTime: return "expired"

  delta = itemTime - now
  days = delta.days
  hours, rem = divmod(delta.seconds, 3600)
  minutes, seconds = divmod(rem, 60)
  
  out = ""
  if days: out += str(days) + "d "
  if hours: out += str(hours) + "h"
  if minutes: out += str(minutes) + "m"
  if seconds: out += str(seconds) + "s"
  
  return out.strip()

jinja.filters['datetime'] = datetime_filter
jinja.filters['timeout'] = timeout_filter