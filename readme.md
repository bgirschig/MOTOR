# MOTOR
A collection of tools for rendering and publishing videos on demand

## commands
```bash
# deploy gcloud services
gcloud app deploy **/app.yaml --project kairos-motor --quiet
```

## Resources
- [todo / issues](https://github.com/bgirschig/MOTOR/issues)
- [design doc][0] (describes services and how they interract)
- [worklog][1] (What is being done, what has been tested)

## Services
- Default: mail handling (has to be default service), task callback (for now),
results page (for now), cron jobs (remove?)
- Console: frontend for admins (edit forms, template management, ...) and maybe
users (request renders, view costs, etc...)
- Forms_service: Generic forms rendering and handling
- Render_service: fulfills render requests

[0]: https://docs.google.com/document/d/1xDYAMEzK8IDPYILng-kyA15-Khsxr7HlmrzoduTy7lk/edit
[1]: https://docs.google.com/document/d/1JxtRm9Li2JE2ljsibqDyBK7jtxVXf5vXMHP_Een1Uy0/edit