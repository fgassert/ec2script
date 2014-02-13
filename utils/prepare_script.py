#!/usr/bin/env python

import sys, getopt

OPTIONS = {
    "-s":"remote_script",
    "-i":"iam_role_name",
    "-r":"aws_default_region",
    "-u":"email_username",
    "-p":"email_password",
    "-e":"email_recipient",
    "-v":"email_server",
    "-t":"shutdown",
    "-o":"save_to_file",
    "-m":"metavars"
}

DEFAULTS = {}

def wrap_script(remote_script=None, iam_role_name=None, aws_default_region=None, email_username=None, email_password=None, email_recipient=None, email_server=None, shutdown=None, save_to_file=None, metavars=None):
    if (remote_script is None or len(remote_script)<8 or 
       remote_script[:4]!="http"):
        
       print "Remote script required (must begin with http:// or https://)"
       print_usage()
       sys.exit()

    out = "#!/bin/bash \ncd ~"
    if iam_role_name is not None:
        out += """
# get jq for json queries
curl -O http://stedolan.github.io/jq/download/linux64/jq
chmod +x jq
 
# get security credentials from instance metadata
curl -o security-credentials.json http://169.254.169.254/latest/meta-data/iam/security-credentials/%s/
 
export AWS_ACCESS_KEY_ID=$(cat security-credentials.json | ./jq -r '.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat security-credentials.json | ./jq -r '.SecretAccessKey')
export AWS_SECURITY_TOKEN=$(cat security-credentials.json | ./jq -r '.Token')
  
# Write to .awscli
echo '[default]' > .awscli
echo aws_access_key_id=$AWS_ACCESS_KEY_ID >> .awscli
echo aws_secret_access_key=$AWS_SECRET_ACCESS_KEY >> .awscli
echo aws_security_token=$AWS_SECURITY_TOKEN >> .awscli
    
# Write to .s3cfg
echo '[default]' > .s3cfg
echo access_key=$AWS_ACCESS_KEY_ID >> .s3cfg
echo secret_key=$AWS_SECRET_ACCESS_KEY >> .s3cfg
echo access_token=$AWS_SECURITY_TOKEN >> .s3cfg
""" % (iam_role_name)
        if aws_default_region is not None:
            out +="""
export AWS_DEFAULT_REGION=%s
echo region=$AWS_DEFAULT_REGION >> .awscli
""" % (aws_region)
    if metavars is not None:
        try:
            pairs = metavars.split(",")
            kvs = [p.split(":") for p in pairs]
            for k,v in kvs:
                out += "\nexport %s=%s" % (k,v)
        except:
            print "metavariables must be a comma separated list of KEY:VALUE pairs"
            sys.exit()
    out += """
# log commands
set +x

# duplicate syslog in user-data.log and /dev/console 
# make available to ec2-get-console-output
exec > >(tee ./user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

# Download remote script and make it executable
curl -o remote_script %s
chmod +x remote_script
./remote_script
""" % remote_script
    if email_username is not None and email_password is not None:
        recipient = ''
        if email_recipient is not None:
            recipient = "-t %s" % email_recipient
        server = ''
        if email_server is not None:
            server = "-r %s" % email_server
        out += """
tar czf ec2log.tgz user-data.log

curl -O https://raw.github.com/fgassert/ec2script/master/utils/send_email.py
chmod +x send_email.py
# Send the logs to yourself!
./send_email.py -u %s -p %s %s %s -s 'Your job is complete' -b 'Executed: %s\n' -a ec2log.tgz
""" % (email_username, email_password, recipient, server, remote_script)

    if shutdown is not None:
        out += """
sudo shutdown -h now
"""
    if save_to_file is not None:
        f = open(save_to_file,'w')
        f.write(out)
        f.close()
    else:
        print out

def print_usage():
   print 'Usage:\tprepare_script.py -s <remote-script> [options]'
   print '\tprepare_script.py -h for help'

def print_help():
   print_usage()
   print "\nPrepare an ec2 startup script to wrap, log, and email the results of executing a remotely hosted script"
   print "\nOptions:"
   for k,v in OPTIONS.iteritems():
      print "    %s <%s>" % (k,v)

def main(argv):      

   in_args = DEFAULTS
   
   # get command line args
   try:
      opts, args = getopt.getopt(argv, "hs:i:r:u:p:e:v:tom:", [])
   except getopt.GetoptError:
      print_usage()
      sys.exit()

   for opt, value in opts:
      if opt == '-h':
         print_help()
         sys.exit()
      if opt in OPTIONS:
         in_args[OPTIONS[opt]]=value

   # pass arg dict as function parameters
   wrap_script(**in_args)

if __name__ == '__main__':
   main(sys.argv[1:])
