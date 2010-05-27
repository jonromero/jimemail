import logging, email
import wsgiref.handlers
import exceptions

from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("================================")
        logging.info("Received a mail_message from: " + mail_message.sender)
        logging.info("The email subject: " + mail_message.subject)
        logging.info("The email was addressed to: " + str.join(mail_message.to, ', '))

        try:
            logging.info("The email was CC-ed to: " + str.join(mail_message.cc, ', '))
        except exceptions.AttributeError :
            logging.info("The email has no CC-ed recipients")

        try:
            logging.info("The email was send on: " + str(mail_message.date))
        except exceptions.AttributeError :
            logging.info("The email has no send date specified!!!")

        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')

        for content_type, body in html_bodies:
            decoded_html = body.decode()
            logging.info("content_type: " + content_type)
            logging.info("decoded_html: " + decoded_html)
            plaintext_bodies

        attachments = []
        # hasattr(a, 'property')
        # http://stackoverflow.com/questions/610883/how-to-know-if-an-object-has-an-attribute-in-python
        try:
            if mail_message.attachments :
                if isinstance(mail_message.attachments[0], basestring):
                    attachments = [mail_message.attachments]
                else:
                    attachments = mail_message.attachments
        except exceptions.AttributeError :
            logging.info("This email has no attachments.")

        logging.info("number of attachments: " + str(len(attachments)))

        for filename, content in attachments:
            #logging.info("plaintext_bodies: " + plaintext_bodies)
            logging.info("filename: " + filename)
            content

        logging.info("--------------------------------")



def main():
    application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
