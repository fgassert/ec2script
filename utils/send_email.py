#!/usr/bin/env python

# A simple command line utility to send an email via SMTP. If no server or recipient are specificed, defaults to sending from a gmail account to itself.

import os, sys, getopt, smtplib, getpass
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

OPTIONS = {
   "-u":"username",
   "-p":"password",
   "-r":"server",
   "-s":"subject",
   "-b":"body",
   "-a":"attachment",
   "-t":"to"
}
DEFAULTS = {
   'server':'smtp.gmail.com:587' 
}

def send_email(username=None, password=None, server=None, subject='', body='', attachment=None, to=None):
   if username is None or password is None:
      print "Username and password required"
      print_usage()
      sys.exit()

   if to is None or len(to) == 0:
      to = username

   message = MIMEMultipart()
   message['From']    = username 
   message['To']      = to 
   message['Subject'] = subject 

   message.attach(MIMEText(body))
   part = MIMEBase('application', 'octet-stream')
   
   if attachment is not None:
      part.set_payload(open(attachment, 'rb').read())
      Encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="%s"'
                      %os.path.basename(attachment))
      message.attach(part) 

   server = smtplib.SMTP(server)
   server.starttls()
   try:
      server.login(username, password)
      server.sendmail(username, to.split(","), message.as_string())
      server.quit()
      print "Email sent to %s" % to
   except Exception as e:
      print e

def print_usage():
   print 'Usage:\tsend_gmail.py -u <username> -p <password> [options]'
   print '\tsend_gmail.py -h for help'

def print_help():
   print_usage()
   print "\nSend an email via SMTP. If no server or recipient are specificed, defaults to sending from a gmail account to itself."
   print "\nOptions:"
   for k,v in OPTIONS.iteritems():
      print "    %s <%s>" % (k,v)

def main(argv):      

   in_args = DEFAULTS
   
   # get command line args
   try:
      opts, args = getopt.getopt(argv, "hu:p:s:r:b:a:t:", [])
   except getopt.GetoptError:
      print_usage()
      sys.exit()

   for opt, value in opts:
      if opt == '-h':
         print_help()
         sys.exit()
      if opt in OPTIONS:
         in_args[OPTIONS[opt]]=value

   # request hidden password if none provided
   if 'password' not in in_args:
      in_args['password']=getpass.getpass()

   # pass arg dict as function parameters
   send_email(**in_args)

if __name__ == '__main__':
   main(sys.argv[1:])
