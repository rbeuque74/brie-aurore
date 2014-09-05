#coding: utf-8
from cStringIO import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import Charset
from email.generator import Generator
import smtplib

class SmtpHelper:

	@staticmethod
	def send_email(from_address, recipient, subject, text):
		# Default encoding mode set to Quoted Printable. Acts globally!
		Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')
		 
		# 'alternative’ MIME type – HTML and plain text bundled in one e-mail message
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "%s" % Header(subject, 'utf-8')
		# Only descriptive part of recipient and sender shall be encoded, not the email address
		msg['From'] = "\"%s\" <%s>" % (Header(from_address[0], 'utf-8'), from_address[1])
		msg['To'] = "\"%s\" <%s>" % (Header(recipient[0], 'utf-8'), recipient[1])
		 
		# Attach both parts
		textpart = MIMEText(text, 'plain', 'UTF-8')
		msg.attach(textpart)
		 
		# Create a generator and flatten message object to 'file’
		str_io = StringIO()
		g = Generator(str_io, False)
		g.flatten(msg)
		# str_io.getvalue() contains ready to sent message
		 
		# Optionally - send it – using python's smtplib
		# or just use Django's

		smtpObj = smtplib.SMTP('smtp.u-psud.fr')
		smtpObj.sendmail(from_address[1], recipient[1], str_io.getvalue())
		#except SMTPException:
        #   print "Error: unable to send email"
        #   raise Exception("Mail non envoyé")

	#end def
#end class