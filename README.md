# ece1779-a3
## Group members
* Hongyu Liu 1005851295   
* Ran Wang 1006126951   
* Zixiang Ma 1005597285  
## Description of the application
This application intends to help people deepen their connections with others in the neighborhood. Sometimes, we want to play basketball while there's no teammates. People who feel lonely in the neighborhood may need company for a walk or a meal. Research has shown that loneliness is found throughout society, including among people in marriages along with other strong relationships, and those with successful careers. Therefore, this application aims to create opportunities for people in the neighborhood to connect with each other and have fun during the activities.

People can post events on this website as hosts, they can also join others' events. The events could be sports, entertainment, or daily routines like walking a dog. There's a map on the website that shows where the events are taking place at, which makes it convenient for people to look for the events that are close to them. Once they are interested, they can view the event details and go through the host's profile where shows the ratings of the events that the host has hosted before. They are able to leave messages for the host if they have questions or comments. They could also rate the event they joined after it finished. 

This application is helpful for those who want to have some connections with others while do not have many friends. It makes sense to join an event in the neighborhood since people would not have to drive a long way for an activity. This application allows users to communicate with hosts and to view the ratings of hosts' past events, which helps ensure that people could join the proper events. Hopefully, people can live a more colorful and happier life by attending the amazing events they shared with others on the website.



## Quick Start

### Set up virtual environment
~~~
python -m venv venv
source venv/bin/activate
~~~
### Install requirements and dependencies
~~~
pip install -r requirements.txt
~~~
### Initialize Zappa settings
~~~
zappa init
~~~
This initializes zappa_settings.json
~~~
{
    "dev": {
        "app_function": "app.webapp",
        "aws_region": "us-east-1",
        "profile_name": "default",
        "project_name": "ece1779-a3",
        "runtime": "python3.8",
        "s3_bucket": "zappa-zb30x62ln",
        "keep_warm":false
    }
}
~~~

### Deploy lambda function 
For first-time deploy
~~~
zappa deploy dev
~~~
For updates
~~~
zappa update dev
~~~





## Architecture of the application
![system architecture](/figures/architecture.png)

### Application and AWS Lambda
The WSGI-compatible Python application 'neighbor' is deployed on AWS Lambda function and API Gateway using Zappa, which makes this an AWS serverless app. By default, Zappa creates an identity and access management (IAM) policy that provides enough permissions to get started, including access to S3 and DynamoDB. A request from an HTTP client will be accepted by the API Gateway and processed by the Lambda function, during which there could be read/write operations to DynamoDB and S3.

### Background process
There is a scheduler that is deployed on EC2 and scheduled to run every hour and triggers event notification and garbage collection functions.

#### Event notification
Scheduler would trigger an lambda function, which would check the DynamoDB to see if there is any event to be started within one hour. If there is, this lambda function will send email notifications to all participants and host.

#### Garbage collection
Scheduler would check the DynamoDB to see if there is any event passes its scheduled time and no longer active. It there is, update the database to change the status to be inactive as a soft delete.

### Functions and user interfaces
![mainPage] need a figure with locations flagged (put this to landing page?? new event= =)

The main page shows events locations on a map and basic events information in a table. Users are able to select how many event entries to show on this page and search events by key words. Users can sort the events in the table by title, type, location, start time, end time and host through clicking the arrows in the header.

![createEvent] need a figure for this (not robust)

Users can create an event by entering the information of it, like title, type, location, number of participants required, start time and end time.

Without logging in, users are able to view the events, however, they need to login to the application before making any further operation. 

![login](/figures/login.png)

If users are new to the application, they need to register first. They can register without a profile image, in that case, the default one will be used.

![register](/figures/register.png)

![eventDetails] people who haven't join cannot rate;

Click the title of the event on the main page will lead to the page that shows event details. Users can see the location on the map, view event details and host information. They can also click the buttons to leave a message to the host, join the event and rate the event.

![Message] 

If users click the button "Message host" on the page that shows event details, they will be led to the message page where there's a contact list on the left and history messages with that host on the right. If users click 'Message' on the navigation bar, the message page will only show the contact list. Once a contact is chosen, the messages on the left will be refreshed.

![Profile] 
The profile page shows user's information and the events that the user has hosted and joined.


### Background process

#### Event notifications
For any event that is scheduled to be held within one hour, this application would automatically send emails to all participants and host. Users would be specifically notified the event title they signed up for and the scheduled time. 

![email](/figures/email.png)

#### Garbage collection
For any event that its start time has passed, the status is updated to be inactive as a soft delete. These events won't be displayed to users anymore.


## Cost model for AWS costs

