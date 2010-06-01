import logging, email
import wsgiref.handlers
import exceptions
from datetime import date

from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class Tag(db.Model):
	body = db.TextProperty(required=True)
	tag = db.CategoryProperty(required=True)
	email = db.EmailProperty(required=True)
	deadline = db.DateProperty()
	created_at = db.DateProperty()

class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
		result = process_email(mail_message)

		if result:
			mail.send_mail(sender=mail_message.to,
						   to=mail_message.sender,
						   subject="You asked for some tags",
						   body=result)


def return_tag_command(subject):
	"""
	Returns tag contents
	get tag1, tag2, tag3 -> due_date
	get    # returns all tags 
	"""

	(tags, deadline) = parse_subject(subject)

	tag = find_tag(user, tags, deadline)
	if tag:
		return tag
	else:
		return "Not found", tag
	

def find_tag(user, tags, deadline):
	if tags:
		return db.GqlQuery("SELECT * FROM Tag WHERE email = :1 and tag = :2 and deadline = :3", user, tags, deadline)
	else: #return all tags
		return db.GqlQuery("SELECT * FROM Tag WHERE email = :1", user)


def add_tag(user, tags, deadline, body):
	if tags == list():
		for tag in tags:
			add_tag(user, tags, deadline, body)
	else:
		t = Tag(email=user, tag=tags, deadline=deadline, body=body) if deadline else Tag(email=user, tag=tags, body=body)
		t.created_at = date.today()
		t.put()
		
	
def process_email(email):
	"""
	Adds/Updates new tags
	"""

	# check if its a command to retrieve messages
	if 'get' in email.subject:
		return return_tag_command(email.subject.split('get')[1])


	(tags, deadline) = parse_subject(email.subject)

	user = email.sender
	body = ""
	for content_type, ebody in email.bodies('text/plain'):
		body += ebody.decode()
	
	#tag = find_tag(user, tag, deadline)
	#if tag:
	#	update_status_tag(tag, body)
	#else:	
	add_tag(user, tags, deadline, body)

	return None
	
def parse_subject(subject):
	"""
	Returns types of email (tags)
	Example: 'todo, idea -> 14/05/2010'
	"""
	deadline = None
	tags = None
	
    # we have a deadline
	if '->' in subject:
		tags, deadline = subject.split('->')
		tags = tags.split(',') if ',' in tags else tags
	else:
		tags = subject.split(',') if ',' in subject else subject
	
	return (tags, deadline)
	
def main():
    application = webapp.WSGIApplication([EmailHandler.mapping()], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()


