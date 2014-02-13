ec2script
=========

Simple command line utility for executing scripts on AWS EC2 instances. Standard AWS charges apply. See http://aws.amazon.com.

Requires: Python, [boto](http://boto.readthedocs.org/en/latest/getting_started.html)

### Quick and dirty setup

```
git clone https://github.com/fgassert/ec2script.git
cd ec2script
sudo make
ec2script --configure
```

### Usage

Launch an EC2 instance with an attached user data script

`ec2script <path-to-script> [options]`

Request an EC2 spot instance with an attached user data script

`ec2script <path-to-script> --spot=PRICE [options]`

List current EC2 spot prices

`ec2script --prices`

If you cancel a command via `ctrl-c` before the requested instances are ready. The script will attempt to cancel your requests.

```
$ ec2script examples/example.sh --spot=10.00
Placing spot requests
sir-6f000000: Your Spot request has been submitted for review, and is pending ev
aluation.
................................................................................
................................................................................
...........................
sir-6f000000: Your Spot request is pending fulfillment.
..................................................^C
Inturrupted...
Canceling spot instance requests...
Terminated: sir-6f000000
```

### An example:

See a [starter user data script](https://github.com/fgassert/ec2script/blob/master/examples/example.sh). 

Run an EC2 instance with the script:

```
$ ec2script examples/example.sh
Launching instance i-e0000000.........................
i-e0000000 : 54.237.0.1
```

Check the console output with [aws-cli](https://github.com/aws/aws-cli/) after the script has completed:

`$ aws ec2 get-console-output --instance-id=i-e0000000`

```
{
    "InstanceId": "i-e0000000",
    "Timestamp": "2014-01-18T06:06:01.000Z",
    "Output": "Xen Minimal OS!\r\n ... [log data] ... System halted.\r\n"
}
```
