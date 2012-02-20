import smtplib
import email
import email.mime.text
import subprocess

MAIL_CONFIGURED = False
MAIL_HOST = None
MAIL_PORT = None
MAIL_USER = None
MAIL_PASS = None

def send_mail(host, port, username, password, msg_from, msg_to, msg_subject, msg_body):
	msg = email.mime.text.MIMEText(msg_body)
	msg['To'] = msg_to
	msg['From'] = msg_from
	msg['Subject'] = msg_subject

	smtp = smtplib.SMTP_SSL(host, port)
	try:
		#smtp.set_debuglevel(True)
		#smtp.ehlo()
		#smtp.starttls()
		#smtp.ehlo()
		smtp.login(username, password)
		smtp.sendmail(msg_from, [msg_to], msg.as_string())
	finally:
		smtp.quit()	
	
def send_email(msg_from, msg_to, msg_subject, msg_body):
	return send_mail(MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASS, 
		msg_from, msg_to, msg_subject, msg_body)

def run(cmd, stdin=None):
	import subprocess
	if stdin:
		p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		p.stdin.write(stdin)
		p.stdin.close()
	else:
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)	
	return p.stdout.read()

if __name__ == '__main__':
	#MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASS = 'smtp.gmail.com', 465, 'XXX', 'XXX'
	#send_email('XXX', 'XXX', 'test subject', 'test body')
	
	
	pass
