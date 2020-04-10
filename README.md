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
### Background process
There is a scheduler that is deployed on EC2 and scheduled to run every hour and triggers event notification and garbage collection functions.

#### Event notification
Scheduler would trigger an lambda function, which would check the DynamoDB to see if there is any event to be started within one hour. If there is, this lambda function will send email notifications to all participants and host.

#### Garbage collection
Scheduler would check the DynamoDB to see if there is any event passes its scheduled time and no longer active. It there is, update the database to change the status to be inactive as a soft delete.
### Functions and user interfaces

### Background process

#### Event notifications
For any event that is scheduled to be held within one hour, this application would automatically send emails to all participants and host. Users would be specifically notified the event title they signed up for and the scheduled time. 

![email](/figures/email.png)

#### Garbage collection
For any event that its start time has passed, the status is updated to be inactive as a soft delete. These events won't be displayed to users anymore.


## Cost model for AWS costs

