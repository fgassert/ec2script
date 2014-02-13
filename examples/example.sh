#!/bin/bash

# log commands
set -x
# duplicate syslog in user-data.log and /dev/console 
# make available to ec2-get-console-output
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

# Go to HOME dir (/root)
cd ~

# If you assigned an instance profile IAM role
ROLE=myrole
# You can retrieve the credentials here
curl -o credentials.json http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE/

# Rather than putting everything in the user-data script we can host setup scripts on github
REMOTE_SCRIPT=https://raw.github.com/fgassert/ec2script/master/hello.sh
# Download remote script and make it executable
curl -o remote_script $REMOTE_SCRIPT
chmod +x remote_script

##########################
# execute the script
./remote_script

##########################

# Once we're done:
# Zip up the log
# Here we can either upload the log to S3 or email it to ourselves
tar czf log.tgz /var/log/user-data.log

##########################
# For example:
# Grab a simple email script
#curl -O http://raw.github.com/fgassert/Email-Self-Script/master/utils/send_email.py
#chmod +x send_email.py
#USER=example@example.com
#PASS=password
#SMTP=smtp.example.com:587
# Send the logs to yourself!
#./send_email.py -u $USER -p $PASS -s "Your job is complete" -b "Executed: $REMOTE_SCRIPT" -a log.tgz
##########################

# Shutdown the instance
sudo shutdown -h now

# You can still access the logs for about an hour after termination via the API ec2-get-console-output
