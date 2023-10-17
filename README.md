# Blog# Page# App# # Django# # on# AWS# Environment
Setting up the entire infrastructure and deploying the application on AWS involves a series of steps and numerous AWS CLI commands. Below, I will provide you with a high# level outline of each step along with the AWS CLI commands you can use to perform these tasks.

 ![Project](project.jpg)

#  Step 1: Create dedicated VPC and whole components
Create the VPC
aws ec2 create# vpc # # cidr# block 10.0.0.0/16

 Create two Availability Zones (AZs)
aws ec2 create# subnet # # vpc# id <VPC_ID> # # cidr# block 10.0.0.0/24 # # availability# zone <AZ1>
aws ec2 create# subnet # # vpc# id <VPC_ID> # # cidr# block 10.0.1.0/24 # # availability# zone <AZ2>

 Create an Internet Gateway
aws ec2 create# internet# gateway

 Attach the Internet Gateway to your VPC
aws ec2 attach# internet# gateway # # vpc# id <VPC_ID>

 Create a NAT Gateway (for one public subnet)
aws ec2 create# nat# gateway # # subnet# id <Public_Subnet_ID> # # allocation# id <EIP_Allocation_ID>

Create public and private route tables
aws ec2 create# route# table # # vpc# id <VPC_ID>
aws ec2 create# route# table # # vpc# id <VPC_ID>

 Create a route to the Internet Gateway for the public route table
aws ec2 create# route # # route# table# id <Public_Route_Table_ID> # # destination# cidr# block 0.0.0.0/0 # # gateway# id <Internet_Gateway_ID>

Associate public and private subnets with the route tables
aws ec2 associate# route# table # # subnet# id <Public_Subnet_ID> # # route# table# id <Public_Route_Table_ID>
aws ec2 associate# route# table # # subnet# id <Private_Subnet_ID> # # route# table# id <Private_Route_Table_ID>

# Step2:Create Security Groups (ALB # # # > EC2 # # # > RDS)

 Create security groups with appropriate inbound rules
aws ec2 create# security# group # # group# name ALBSecurityGroup # # description "ALB Security Group" # # vpc# id <VPC_ID>
aws ec2 create# security# group # # group# name EC2SecurityGroup # # description "EC2 Security Group" # # vpc# id <VPC_ID>
aws ec2 create# security# group # # group# name RDSSecurityGroup # # description "RDS Security Group" # # vpc# id <VPC_ID>

 Configure security group inbound rules (e.g., allow HTTP/HTTPS)
aws ec2 authorize# security# group# ingress # # group# id <ALB_Security_Group_ID> # # protocol tcp # # port 80 # # source 0.0.0.0/0
aws ec2 authorize# security# group# ingress # # group# id <ALB_Security_Group_ID> # # protocol tcp # # port 443 # # source 0.0.0.0/0

Repeat the above commands for EC2 and RDS security groups with appropriate rules.

# Step 3: Create RDS

 Create an RDS instance
aws rds create# db# instance # # db# instance# identifier <DB_Instance_Name> # # db# instance# class db.t2.micro # # engine mysql # # engine# version 8.0.20 # # allocated# storage 20 # # vpc# security# group# ids <RDSSecurityGroupID> # # availability# zone <AZ>

# Step4 : Create two S3 Buckets and set one of these as static website


 Create the first S3 bucket for regular use
aws s3api create# bucket # # bucket <Bucket1Name> # # region <YourRegion>

 Create the second S3 bucket for the static website
aws s3api create# bucket # # bucket <Bucket2Name> # # region <YourRegion>

 Configure the second bucket for static website hosting
aws s3 website s3://<Bucket2Name> # # index# document index.html # # error# document error.html

 Optionally, you can upload your static website content to the second bucket
aws s3 cp <local_static_website_directory> s3://<Bucket2Name> # # recursive

#  Step 5: Download or clone the project definition 
  
  git clone  https://github.com/Salim1bechraoui/Blog# Page# App# # Django# # on# AWS# Environment.git

# Step 7: Prepare a userdata to be utilized in Launch Template
 
 ./userdata.sh

# Step 8: Write RDS, S3 in settings file given by Fullstack Developer team

In this step, you will need to configure your Django application's settings to connect to the RDS database and use the S3 buckets for storing and retrieving files. You will typically do this in your Django project's settings.py file.
 Open blogapp/settings.py

S3 Configuration:

In the same settings.py file, find or create a section related to file storage or media storage. It may look like this:

AWS_STORAGE_BUCKET_NAME = '<bucket_name>'
AWS_S3_REGION_NAME = '<bucket_region>'
AWS_ACCESS_KEY_ID = '<access_key_id>'
AWS_SECRET_ACCESS_KEY = '<secret_access_key>'

In the settings.py file, ensure that you've configured the static and media URL settings:
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

Make sure your project is using the appropriate storage backends for both static files and media files. For example:

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

After configuring your settings, you'll need to collect static and media files to the S3 buckets. Use the following commands:

python manage.py collectstatic
python manage.py migrate

# Step 9: Create NAT Instance in Public Subnet

aws ec2 run# instances \
  image# id <NAT_Instance_AMI_ID> \
  instance# type <Instance_Type> \
  key# name <Key_Pair_Name> \
  subnet# id <Public_Subnet_ID> \
  associate# public# ip# address

You'll need to create a security group for your NAT instance that allows outbound traffic (e.g., all ports) and inbound traffic for responses. Here's an example using the AWS CLI:

aws ec2 create# security# group \
  group# name NATSecurityGroup \
  description "NAT Security Group" \
 vpc# id <VPC_ID>

aws ec2 authorize# security# group# ingress \
  group# id <NAT_Security_Group_ID> \
  protocol # 1 \
  source# group <NAT_Security_Group_ID>

By default, source/destination checking is enabled on EC2 instances. You should disable it for your NAT instance:

aws ec2 modify# instance# attribute \
 instance# id <NAT_Instance_ID> \
 no# source# dest# check

The next step is to update the route tables to route internet# bound traffic through the NAT instance. This will require updating the route table associated with your private subnets.

aws ec2 create# route \
 route# table# id <Private_Route_Table_ID> \
 destination# cidr# block 0.0.0.0/0 \
 instance# id <NAT_Instance_ID>

#  Step10: Create Launch Template and IAM role for it 
  
  aws iam create# role \
  role# name <Role_Name> \
  assume# role# policy# document file://role# policy.json

Create a JSON policy document that defines what services the role can access and the permissions. For example:
 check s3policy.json

Attach policies to the role based on the permissions your instances need. For instance, if your instances need access to S3 and DynamoDB, you can attach the appropriate policies:

aws iam attach# role# policy \
  role# name <Role_Name> \
  policy# arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach# role# policy \
  role# name <Role_Name> \
  policy# arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

Creating a Launch Template:

Use the AWS CLI to create a Launch Template with the IAM role you just created: 

aws ec2 create# launch# template \
  launch# template# name <Template_Name> \
  version# description <Template_Version_Description> \
  launch# template# data file://launch# template.json

Create a JSON file that specifies the configuration details for your EC2 instances, including the IAM role. An example might look like this

{
  "BlockDeviceMappings": [
    {
      "DeviceName": "/dev/sda1",
      "Ebs": {
        "VolumeSize": 8,
        "VolumeType": "gp2"
      }
    }
  ],
  "InstanceType": "t2.micro",
  "KeyName": "YourKeyPairName",
  "IamInstanceProfile": {
    "Arn": "arn:aws:iam::123456789012:instance# profile/YourIAMRoleName"
  },
  "UserData": "Base64# encoded user data (if needed)"
}

You can now launch an EC2 instance using the Launch Template:

aws ec2 run# instances # # launch# template LaunchTemplateName=<Template_Name>,Version=1

Step 11: Create certification for secure connection: 


To create a certificate for secure connections (typically for SSL/TLS encryption) in AWS, you can use the AWS Certificate Manager. Here are the steps to create a certificate:

Using the AWS Management Console:

Log in to the AWS Management Console.

Navigate to AWS Certificate Manager:

In the AWS Management Console, search for "Certificate Manager" or locate it under the "Security, Identity, & Compliance" section.
Request a Public Certificate:

Click the "Request a certificate" button.
Select "Request a public certificate" and click "Next."
Add Domain Names:

Enter the domain names (e.g., example.com and www.example.com) for which you want the certificate.
Click "Next."
Choose Validation Method:

Choose how you want to validate domain ownership:
DNS validation: You'll need to create DNS records.
Email validation: AWS sends validation emails to domain owner email addresses.
Follow the instructions for the chosen method.
Review and Confirm:

Review the domain names and validation method.
Click "Confirm and request."
Validation:

Complete the domain validation process as per the selected method. DNS records or email validation links may be required.
Certificate is Issued:

Once validation is successful, your certificate will be issued.
Using the AWS CLI:

If you prefer to use the AWS CLI, you can create a certificate with the create# certificate command. Here's an example command:

aws acm request# certificate # # domain# name example.com # # subject# alternative# names www.example.com


# Step12: Create ALB and target Group 

To create an Application Load Balancer (ALB) and a Target Group in AWS, follow these steps:

Creating an Application Load Balancer (ALB):

Log in to the AWS Management Console.

Navigate to EC2:

In the AWS Management Console, go to the EC2 Dashboard.
Create an Application Load Balancer:

In the EC2 Dashboard, click on "Load Balancers" in the navigation pane.
Click the "Create Load Balancer" button.
Configure Load Balancer:

Choose "Application Load Balancer" as the load balancer type.
Configure the Load Balancer settings, including a name, a VPC, and listeners (e.g., HTTP on port 80 or HTTPS on port 443).
Define the security group for the ALB, which should allow incoming traffic on the listener port (e.g., HTTP/80 or HTTPS/443).
Configure the routing options, which will depend on your specific application setup.
Configure Security Settings (if using HTTPS/SSL):

If you're using HTTPS, you can configure SSL/TLS settings, including choosing or uploading an SSL certificate.
If you're using a certificate from AWS Certificate Manager, you can select it here.
Configure Security Policies (if using HTTPS/SSL):

Select an appropriate security policy based on your application's security requirements.
Review and Create:

Review your configuration settings and click "Create" to create the ALB.
Creating a Target Group:

After creating the ALB, navigate to the Target Groups section under the Load Balancer details.

Create a Target Group:

Click the "Create target group" button.
Configure Target Group:

Provide a name for the Target Group.
Specify the protocol (e.g., HTTP or HTTPS).
Choose the VPC.
Set the target type (e.g., instances or IP addresses).
Configure health checks, specifying the path and protocol used for health checks.
Register Targets:

Register the targets (EC2 instances) that the ALB will route traffic to. You can do this manually or use an existing Auto Scaling group if you're using auto# scaling.
Create the Target Group:

Review your settings and click "Create."
Now, the Application Load Balancer and Target Group are created and configured. You can associate the Target Group with the ALB's listener rules to route traffic to your instances or services based on your application's requirements.

Remember to adjust your security group rules for the EC2 instances to allow traffic from the ALB. Additionally, you may need to configure DNS settings to point your domain to the ALB's DNS name for public access.

#  Step 13: Create Autoscaling Group with Launch Template

Log in to the AWS Management Console.

Navigate to the Auto Scaling Service:

In the AWS Management Console, search for "Auto Scaling" or locate it under "Compute" in the services menu.
Create an Auto Scaling Group:

Click on "Auto Scaling Groups" in the navigation pane.
Click the "Create Auto Scaling group" button.
Choose Launch Template or Configuration:

Select "Launch Template" as the configuration type.
Choose the Launch Template you created in an earlier step.
Configure Group Details:

Provide a name for your Auto Scaling group.
Specify the desired capacity (the number of instances you want to start with), minimum and maximum instance count.
Choose your VPC and subnet(s).
Configure Scaling Policies:

Set up scaling policies for your Auto Scaling group. You can choose target tracking scaling or other scaling policies based on your requirements.
Define scaling policies such as CPU utilization thresholds for scaling in and out.
Configure Instance Protection (optional):

If needed, configure instance protection settings to prevent specific instances from being terminated during scaling operations.
Configure Notifications (optional):

Set up notifications to receive alerts when scaling events occur.
Add Tags (optional):

You can add tags to the instances created by the Auto Scaling group for easier identification.
Configure Instance Termination Policy:

Choose an instance termination policy to determine which instances to terminate when scaling down.
Review and Create:

Review your configuration settings.
Click "Create Auto Scaling group" to create the Auto Scaling group with the specified settings.
The Auto Scaling group will now use the Launch Template you configured to launch and manage instances. Scaling policies will automatically adjust the number of instances in the group based on your defined scaling thresholds and criteria.


