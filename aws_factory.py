import boto3
import json
import time

def createBucket(bucketName):
    print('CREATING BUCKET FOR CLIENT...')
    # Creating bucket
    s3Client = boto3.client('s3')
    s3Client.create_bucket(Bucket=bucketName)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketName)
    bucket.wait_until_exists()
    # Adding bucket policy to allow public access
    bucket_policy = {
     'Version': '2012-10-17',
     'Statement': [{
         'Sid': 'AddPerm',
         'Effect': 'Allow',
         'Principal': '*',
         'Action': ['s3:GetObject'],
         'Resource': "arn:aws:s3:::%s/*" % bucketName
      }]
    }
    bucket_policy = json.dumps(bucket_policy)
    s3Client.put_bucket_policy(Bucket=bucketName, Policy=bucket_policy)
    # Define website default and error pages
    s3Client.put_bucket_website(
        Bucket=bucketName,
        WebsiteConfiguration={
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        }
    )
    print('BUCKET CREATED')

def createInstance(privateKeyName, subnetId, securityGroupId, awsRegion, amiId):
    print('CREATING INSTANCE FOR SERVER...')
    ec2 = boto3.resource('ec2', region_name=awsRegion)

    instances = ec2.create_instances(
        MinCount = 1,
        MaxCount = 1,
        ImageId=amiId,
        InstanceType='t2.micro',
        KeyName=privateKeyName,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'server'
                    },
                ]
            },
        ],
        NetworkInterfaces=[
        {
            'DeviceIndex': 0,
            'SubnetId' : subnetId,
            'Groups': [
                securityGroupId
            ],
            'AssociatePublicIpAddress': True            
        }],
    )
    instanceId = ''
    for instance in instances:
        instance.wait_until_running()
        time.sleep(10)
        print(f'EC2 INSTANCE "{instance.id}" HAS BEEN STARTED')
        instanceId = instance.id
    return instanceId

