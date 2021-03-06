# pylint: disable=E1101

from urlparse import urlparse, parse_qs
import urllib2
from common.storage_utils import upload_image
from googleapiclient import discovery
from google.oauth2 import service_account
from os import path
import math
from common.task_queue_client import Queue

scopes = [
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.metadata.readonly']
credentials = service_account.Credentials.from_service_account_file(
  "app_credentials.json", scopes=scopes)
TASK_QUEUE_API_URL = 'https://task-queue-dot-kairos-motor.appspot.com'

sheets_service = discovery.build('sheets', 'v4', credentials=credentials)
sheets = sheets_service.spreadsheets()
queue = Queue()

def checkSpreadsheet(spreadsheet_id, definition_name):
  result = sheets.values().get(spreadsheetId=spreadsheet_id, range="1:10").execute()
  values = result.get('values', [])
  headers = values[0]

  requests = []
  for line_idx, line in enumerate(values):
    # skip header row (while keeping line_idx consistent)
    if line_idx == 0:
      continue

    item = {}
    for header_idx, header in enumerate(headers):
      if header_idx < len(line):
        item[header] = line[header_idx]
      else:
        item[header] = None
    
    if not "MOTOR id" in item:
      raise KeyError("missing 'MOTOR id' column in spreadsheet. please add it")
    
    if not item["MOTOR id"] and item["Image"] and item["Email Address"]:
      prepare_images(item)
      request = prepare_request(item)
      request["line_idx"] = line_idx + 1 # line idx starts at 1
      requests.append(request)

  update_data = []
  motorColumn = getColName(headers.index("MOTOR id"))
  
  for request in requests:
    task_id = queue.appendTask(request, ["render", "google_form"], 4)["task_key"]
    update_data.append({
      "range": motorColumn+str(request["line_idx"]),
      "values": [[task_id]],
      "majorDimension": "ROWS"
    })

  sheets.values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={"valueInputOption": "USER_ENTERED", "data": update_data},
  ).execute()

  return requests

def getColName(idx):
	while idx>=26:
		return getColName(idx/26-1) + getColName(idx%26)
	return chr(ord('A')+idx)

def prepare_images(item):
  item['Image'] = item['Image'].split(', ')
  for idx, file_url in enumerate(item["Image"]):
    parsed = parse_qs(urlparse(file_url).query)
    file_id = parsed["id"][0]
    drive_url = "https://drive.google.com/uc?authuser=0&id=%s"%file_id
    drive_file = urllib2.urlopen(drive_url)
    gs_url = upload_image(drive_file, 'image/jpeg')
    item['Image'][idx] = gs_url

# TODO: Use a form definition for that
def prepare_request(data):
  data_file = {
    "title": data["Title"],
    "date1": data["Date 1"],
    "date2": data["Date 2"],
    "time": data["Screening Time"],
    "duration": data["Duration"],
    "language": data["Language"],
    "director": data["Directors name"],
  }
  request_payload = {
    "template": "xenix",
    "compName": "main",
    "clientID": data["Email Address"],
    "requesterID": data["Email Address"],
    "resources": [
      {
        "target": "(footage)/data.json",
        "data": data_file,
      },
      {
        "target": "(footage)/01-footage/5378.jpg",
        "src": data["Image"][0],
      },
    ],
    "encoders": [
      "-pix_fmt yuv420p video.mp4"
    ],
  }

  return request_payload
