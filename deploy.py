import os
import boto3
import paramiko
from scp import SCPClient
from aws_factory import createBucket
from aws_factory import createInstance

# CONFIGURATION (TO MODIFY ACCORDING TO YOUR NEEDS)
## FULL PATH TO WEBSITE CLIENT FOLDER
PATHTOCLIENT = 'C:/Users/herme/Documents/Final_project/final_project_2/website/client/' 

## FULL PATH TO WEBSITE SERVER FOLDER
PATHTOSERVER = 'C:/Users/herme/Documents/Final_project/final_project_2/website/server/' 

## AWS EC2 PRIVATE KEY (TO CREATE EC2 INSTANCE)
PRIVATEKEYNAME = 'guilhem' 

## AWS EC2 PRIVATE KEY PATH ON YOUR COMPUTER
PRIVATEKEYPATH = 'C:/Users/herme/Documents/guilhem.pem' 

## CHOICE OF S3 BUCKET NAME
BUCKETNAME = 'finalprojectbucketguilhem' 

## NAME OF THE FILE CONFIGURING API BASE URL FOR WEB PAGES (THE FIRST LINE MUST BE: const baseURL = '$URL';
## WHERE $URL IS YOUR API URL IN DEVELOPMENT MODE (ex: http://localhost:5000/), AND YOU MIGHT USE THIS BASEURL FOR EACH API ACCESS )
ENVJS = 'scripts.js'

# AWS REGION (FOR INSTANCE CREATION)
AWS_REGION = "us-east-1"

# SUBNET ID (FOR INSTANCE CREATION)
SUBNETID = "subnet-0e63a5fa3ab860a29"

# SECURITY GROUP ID (FOR INSTANCE CREATION)
SECURITYGROUPID = 'sg-0e99153c9ba93183a'

## AMAZON MACHINE IMAGE ID (Ubuntu 20.04LTS), SHOULD NOT BE MODIFIED
AMI_ID = 'ami-04505e74c0741db8d'

## NAME OF THE TEMPORARY FILE TO CHANGE ENVIRONMENT VARIABLES (API URL), SHOULD NOT BE MODIFIED
TMPENVFILE = 'tmpEnv.js'

# Changes the base URL of the API from development to production one
def changeEnv(newBaseURLIP):
    f = open(PATHTOCLIENT + ENVJS)
    first_line, remainder = f.readline(), f.read()
    t = open(PATHTOCLIENT + TMPENVFILE,"w")
    t.write('const baseURL = "http://' + newBaseURLIP + '/"\n')
    t.write(remainder)
    t.close()

# Deploys all the client side (web pages, style, javascript, assets,...) on S3
def deploy_client(bucketObject, newBaseURL):
    print('STARTING CLIENT DEPLOYMENT')
    endpoint = 'http://' + BUCKETNAME + '.s3-website-us-east-1.amazonaws.com'
    changeEnv(newBaseURL)
    # Browse all the client side tree structure
    for path, subdirs, files in os.walk(PATHTOCLIENT):
        path = path.replace('\\','/')
        directory_name = path.replace(PATHTOCLIENT,'')
        nonRootSlash = ''
        for file in files:
            if directory_name == '':
                nonRootSlash = ''
            else:
                nonRootSlash = '/'
            relativePath = directory_name + nonRootSlash + file
            # Condition to put back the initial name of the environment JS file, and only deploy the modified one
            if (not relativePath==ENVJS) and (not relativePath == TMPENVFILE):
                # Check if the file is a web page (necessary to open it on browser then)
                if file.split('.')[1]=='html':
                    print('UPLOADING FILE : ' + relativePath + ' as HTML')
                    bucketObject.upload_file(os.path.join(path, file), relativePath, ExtraArgs={'ContentType':'text/html'})
                else:
                    print('UPLOADING FILE : ' + relativePath)
                    bucketObject.upload_file(os.path.join(path, file), relativePath)
            if relativePath==TMPENVFILE:
                print('UPLOADING FILE : ' + relativePath + ' as ' + ENVJS)
                bucketObject.upload_file(os.path.join(path, file), ENVJS)
                os.remove(PATHTOCLIENT + TMPENVFILE)
    print('CLIENT DEPLOYMENT FINISHED, SERVING AT :' + endpoint)

# Deploys all the server side (manage environment, send server file and launch it) on EC2
def deploy_server(instanceObject):
    print('STARTING SERVER DEPLOYMENT')
    print('RETRIEVING INSTANCE IP ADRESS')
    # Get API new IP (instance IP)
    ipaddress = instanceObject.public_ip_address
    print('ip adress: ' + ipaddress)

    print('SSH CONNECTION...')
    # SSH configuration
    key = paramiko.RSAKey.from_private_key_file(PRIVATEKEYPATH)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # SSH connection to the EC2 instance
    client.connect(hostname=ipaddress, username="ubuntu", pkey=key)
    print('CONNECTED TO INSTANCE')

    # Sending server files to the instance (configured for a simple flask API)
    scp = SCPClient(client.get_transport())
    print('SENDING SERVER FILES TO INSTANCE...')
    scp.put(PATHTOSERVER + 'app.py', remote_path="/home/ubuntu")
    print('SENT')
    scp.close()

    # Prepare instance environment in order to run the flask server
    print('PREPARING ENVIRONMENT...')
    environmentCmd = 'sudo apt-get update;sudo apt install -y python3-pip;sudo pip install Flask;sudo pip3 install Flask-Cors'
    stdin, stdout, stderr = client.exec_command(environmentCmd)
    print(stdout.read())
    print('ENVIRONMENT CONFIGURED')

    # Launch server, with nohup to avoid stopping it at SSH connection closing
    print('LAUNCHING SERVER')
    launchCmd = 'nohup sudo flask run --host=0.0.0.0 --port=80 >/dev/null 2>&1 &'
    stdin2, stdout2, stderr2 = client.exec_command(launchCmd)
    print(stdout2.read())
    print('SERVER LAUNCHED')
    client.close()
    print('SERVER DEPLOYMENT FINISHED, RUNNING ON http://'  + ipaddress)
    return ipaddress


# Create S3 bucket
createBucket(BUCKETNAME)
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKETNAME)

# Create EC2 instance
instanceId = createInstance(PRIVATEKEYNAME, SUBNETID, SECURITYGROUPID, AWS_REGION, AMI_ID)
ec2 = boto3.resource('ec2')
instance = ec2.Instance(instanceId)

# Deploy server
serverIP = deploy_server(instance)

# Deploy client
deploy_client(bucket, serverIP)

    