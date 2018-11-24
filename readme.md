# MOTOR
A collection of tools for rendering and publishing videos on demand

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
- handle for output (upload files, call callback, ...)

### rendernode
The worker service for fultilling render requests
TODO: move code to this repo