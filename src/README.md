# NewsPlatform

Notes on the project

## Development

1. Install dependencies with `pip install -r requirements.txt`
2. Run migrations with `python manage.py migrate`

In this repository, the dev branch is used for working on localhost. To run the server for development use: `python manage.py runserver --settings=newsPlatform.settings.development`. The admin user password is `newsplatform`.

## Settings

There are three settings in the projects root folder: **newsPlatform**. One for base settings. One for development (localhost) and one for production (live)

## Apps

There are currently four apps:

1. Articles (CRUD views for articles)
2. Categories (Basic model for category selection on an article)
3. Core (Users, Profiles, Channels, Subscriptions and Payouts)
4. Newsletter (Mailchimp newsletter signups)

## Deployment with AWS

This project is hosted using Elastic Beanstalk. Elastic Beanstalk is a Platform As A Service (PaaS) that streamlines the setup, deployment, and maintenance of your app on Amazon AWS. It’s a managed service, coupling the server (EC2), database (RDS), and your static files (S3).

The project's **src** directory contains two required EB directories - **.ebextensions** and **.elasticbeanstalk**

The **.ebextensions** contains a config file with settings for the Django project. In the config file the following commands are set to execute on deployment:

1. Make migrations to the database
2. Create a superuser
3. Create required model instances
4. Collect static files

The **.elasticbeanstalk** contains a config file specifying settings. The important ones being the default region of the application (us-west-2), the Python version (3.6) and environment (src-prod)

From scratch, the deployment process is as follows:

```
pip install awsebcli
eb init
```

Next it will ask for your AWS credentials. You'll need the keys it asks for, which are found in your AWS dashboard.

Now we create an environment:

```
eb create
```

Follow the prompts to create the environment. Afterwards you can use `eb logs` to see the status of the environment. Note when it gives you the **CNAME** of the environment, we need to add that to the projects allowed sources.

Deploy the app with:

```
eb deploy
```

Open the app in the browser with:

```
eb open
```

Now we create an RDS instance. Navigate to your EB instance and click on the environment that was now created. Click on `configuration` in the side panel. Scroll to the bottom and click `Create a new RDS database`. On the RDS setup page change the DB Engine to postgres and add a username and password (note you won't need to specify these in the app as they are environment variables so Django will read them for you).

If you need to configure something on the server, you can ssh into it with `eb ssh`. When setting up the instance you were probably asked if you'd like to create an ssh key pair. You only need to remember the passphrase for the keypair you created. When using ssh you will be asked to enter the passphrase.

If there are changes to the projects models and you need to makemigrations, you will need to run `eb deploy` with the new code and then handle migrations on the server

## Scheduled task with AWS Lambda

Lambda is a serverless service. You pay for when the code is actually executed. It's free up to 1 000 000 requests per month, so there shouldn't be any costs from this.

The purpose of the lambda script is to call the create payouts view on the server. It is scheduled for the 15th day of each of month at 9:00 AM (UTC). To setup a script follow [this tutorial](https://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example.html).

In the lambda console is a scheduled job created with Python. The cron settings for the scheduled event are `cron(0 9 15 * ? *)`. There are measures in place to check if an error occurs when calling the function - if there is an error an email is sent out to those on the subscriber list.

## Domain management

DNS records were changed from the domain account manager to AWS and can be managed in the Route53 console.
