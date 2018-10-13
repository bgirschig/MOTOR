# render service

## role
- receive all render requests
- keep track of render nodes
- distribute render jobs

## Flow
- receive a render request
- check render request
  - is valid, has all info
  - is properly authenticated
  - client has quota
- push request to a push/pull queue
- receive a lease request from a render node
- lease task from the render queue, return it to the render node
- listen for status events from the render node, delete the task if successful