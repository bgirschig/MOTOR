# Motor - security
This doc lists potential security vulnerabilities, and what's done to prevent
them

## mail
Motor can receive, parse, and add renders to queue from emails
### credentials
current status: No cerdentials are needed for the mail service yet.
possible solution: We could ask the client to use his account to generate a
custom email adress (render-some_id_code@kairos-motor.appspotmail.com) to which
he would send his requests. This gives a reasonnable amout of certainty as to
who sent the email (sender address can be spoofed).
