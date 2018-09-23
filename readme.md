# Mail service

A service for handling render requests sent by mail

## process
- An email is received on render@kairos-motor.appspotmail.com
- The email is parsed. Links in the mail are extracted
- The webpage each link points to is parsed, to retrieve info for the render request
- A render request is created and added to the render queue
- An email response is sent, to confirm the request has been sent, preview the parsed data
- the render is performed
- An email confirmation is sent
