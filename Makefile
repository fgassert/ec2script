install : 
	mkdir /usr/share/ec2script
	cp instance_data.json /usr/share/ec2script/
	chmod +x ec2script
	cp ec2script /usr/local/bin/
	echo "Install complete"

uninstall :
	rm -r /usr/share/ec2script
	rm /usr/local/bin/ec2script
