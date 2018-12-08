# MOTOR
A collection of tools for rendering and publishing videos on demand

## TODO
- unit testing, continuous integration, continuous delivery (mostly for render service)
- user management
- move email logic to own service, and redirect mails from default service there
- analytics
- secure task queue
- shared templates between render nodes: download on request (with cache?)
- node manager: restart, clear cache, etc...
- switch render node to python
  - We chose js because of nexrender, but since we are not using it...
  - would allow sharing some code with other services (mainly task queue client,
  but also exceptions, etc...)
- File management:
  - The dedupliction feature is nice, but there is no way to know if a file is
  still in use (and delete it if it's not).
  - Image service. either:
    - use google's image service
    - create a specific service for image handling, converting, etc...
  - something that works both in dev and in prod
- task queue
  - callbackUrl
  - Exponential backoff
  - reduce delay & ping rate:
    - on worker node startup, notify queue
    - on job, notify one of registered worker
    - if fail because not found unregister worker (__|!|__ what about network error?)
    - if fail for other reason, try other worker
- upload render outputs to cloud storage (instead of ftp)
  - publish is a next step
- pretty error handlers: create formatted error pages

## Services
### Default
handles emails sent to @kairos-motor.appspotmail.com

### Task_queue
manages MOTOR's task queue:
- add a task to the queue
- when a worker node is ready, it pulls from the queue
- when the work is done, status is updated

### forms
handles motor's form needs
- render form from definition
- handle form output (upload files, call callback, ...)

### rendernode
The worker service for fultilling render requests