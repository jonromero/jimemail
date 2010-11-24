import logging, email
import wsgiref.handlers
import exceptions

from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

"""
class Tag(db.Model):
	body = db.TextProperty(required=True)
	tag = db.CategoryProperty(required=True)
	email = db.EmailProperty(required=True)
	created_at = db.DateTimeProperty(auto_now=True)
"""

class Tag(db.Model):
	body = db.StringListProperty(required=True)
	tag = db.CategoryProperty(required=True)
	email = db.EmailProperty(required=True)
	created_at = db.DateTimeProperty(auto_now=True)

class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
		command_response = process_email(mail_message)

		if command_response:
			send_email(mail_message.to, mail_message.sender, mail_message.subject, command_response)
			
					   
def send_email(sender, to, subject, body):
	mail.send_mail(sender=sender,
				   to=to,
				   subject=subject,
				   body=body)


def return_tag_command(user, subject):
	"""
	Returns tag contents
	? tag1, tag2, tag3 -> due_date
	?    # returns all tags 
	"""

	tags, = parse_subject(subject)

	tag = find_tag(user, tags)
	if tag:
		return tag
	else:
		return "Not found", tag
	

def find_tag(user, tags):
	result = []

	if tags:
		if type(tags) == list():
			for tag in tags:
				result += db.GqlQuery("SELECT * FROM Tag WHERE email = :1 and tag = :2", user, tag).fetch(1000)
		else:
			result = db.GqlQuery("SELECT * FROM Tag WHERE email = :1 and tag = :2", user, tags).fetch(1000)
	else: #return all tags
		result = db.GqlQuery("SELECT * FROM Tag WHERE email = :1", user).fetch(1000)


	
	return result

def add_tag(user, tags, body):
	lst_body = [d.strip() for d in body.split("*") if d.strip() != ""]  if "*" in body else [body]

	if type(tags) == list():
		for tag in tags:
			t = Tag(email=user, tag=tag, body=lst_body)
			t.put()
	else:
		t = Tag(email=user, tag=tags.strip(), body=lst_body)
		t.put()

def update_tag(tag, body, erase=False):
	if erase:
		done_items = check_for_done(body)
	else:
		done_items = []
		
	items = [t for t in tag.body]

	if done_items:
		for done_item in done_items:
			items.remove(done_item)
	else:
		items.append(body)
		
	tag.body = items
	tag.put()
	

def check_for_done(body):
	done_items = []
	
	# Break lines that start with '*' to items (skip emtpy lines)
	data = [d.strip() for d in body.split("*") if d.strip() != ""]  if "*" in body else [body]

	# if "done" is found in a line, mark the previous one
	for idx in range(len(data)):
		if "done" in data[idx].lower():
			previous_data = data[idx-1] if idx > 1 else None
			done_items.append(previous_data)

	return done_items
			
	
def find_user(email):
	return db.GqlQuery("SELECT * FROM Tag WHERE email = :1", email).get()


def process_email(email):
	"""
	Adds/Updates new tags
	"""
	# user never used the service before
	# so send him an email with instructions!
	if not find_user(email.sender):
		send_email(email.to, email.sender, "Welcome to thejimemail!", "These are the instructions!")
		
	# check if its a command to retrieve messages
	if '?' in email.subject:
		return return_tag_command(email.sender, email.subject.split('?')[0])

	tags = parse_subject(email.subject)

	user = email.sender
	body = ""
	for content_type, ebody in email.bodies('text/plain'):
		body += ebody.decode()

	# check if its a command to interact messages
	if 're:' in email.subject[0:3].lower():
		return update_tag(tag, body, True)

	# if tag exists, update it
	tag = find_tag(user, tags)
	if tag:
		if type(tag) == list():
			for t in tag:
				update_tag(t, body)
	else:	
		add_tag(user, tags, body)

	return None
	
def parse_subject(subject):
	"""
	Returns types of email (tags)
	Example: 'todo, idea'
	"""
	tags = subject.split(',') if ',' in subject else subject.strip()
	
	return tags
	
def main():
    application = webapp.WSGIApplication([EmailHandler.mapping()], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()


