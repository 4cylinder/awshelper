#!/usr/bin/env python

import subprocess, json, os, argparse

parser = argparse.ArgumentParser(description="Download AWS CloudWatch logs from a specific group, with optional version filtering.")
parser.add_argument('-g', '--group', help="Log Group Name, e.g. /aws/lambda/batman", required=True)
parser.add_argument('-v', '--version', help="Version (default $LATEST)", default="\\$LATEST")
parser.add_argument('-d', '--directory', help="Output Directory (default is your downloads folder)", default="~/Downloads")
parser.add_argument('-o', '--output', help="Output file (if you want all your logs in the same file). Do not include the directory.")

args = parser.parse_args()

def getOutput(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output

groupName = args.group
version = "[%s]" % args.version
directory = args.directory
outfile = args.output

# Pre-emptive corrections
if "~" in directory:
    directory = os.path.expanduser(directory)
if outfile:
    outfile = directory + "/" + outfile

os.system("mkdir %s" % directory)
if outfile: os.system("rm %s" % outfile)
getStreamsCmd = "aws logs describe-log-streams --log-group-name %s" % groupName
loggroup = json.loads(getOutput(getStreamsCmd))
streams = [x['logStreamName'] for x in loggroup['logStreams'] if version in x['logStreamName']]

for stream in streams:
    saved = outfile if outfile else "%s/%s.log" % (directory, stream.split(']')[1])
    print("Saving stream with name %s to file %s" % (stream, saved))
    operator = ">>" if outfile else ">"
    cmd = "aws logs get-log-events --log-group-name %s --log-stream-name %s --output text %s %s;" % (groupName, stream, operator, saved)
    print(cmd)
    os.system(cmd)

print("Done. Your logs are saved in %s" % (outfile if outfile else directory))
