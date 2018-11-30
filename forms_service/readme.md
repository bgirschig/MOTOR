# Forms service

## TODO
- The task_queue_client code is duplicated across services. would be nice to unify that
- Google drive download is Über slow, try solving (...not sure how)
- task_queue_client url depends on service. Should use an env variable

## form definitions
- title: title for the tab, displayed on the page, etc...
- action: Where to send the output of the form, once processed
- template: template name
- etc...
- fields: defines how the fields are displayed on the page, what constraints they have, etc
  - name
  - displayName: the name displayed in the rendered form
  - type: textfield, checkbox, radio, datetime, files
  - choices: (for checkbox and radio types)
    - _other: if you want to allow a free text input as choice
  - constraints:
    - min & max: for datetime. can be 'now', or a datetime string, eg. '2018-11-25T16:38' 
    - minCount & maxCount: for files
    - maxSize: for files
- output: Defines how the data is structured before sending to the 'action' url.
  - example:
    data:
      field_title: title
      field_tags: tags/multi