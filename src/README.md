# NewsPlatform

Notes on the project

## Development

1. Install dependencies with `pip install -r requirements.txt`
2. Run migrations with `python manage.py migrate`
3. Run the server

### Settings

There are three settings in the projects root folder: **newsPlatform**. One for base settings. One for development (localhost) and one for production (live)

### Apps

There are currently four apps:

1. Articles (CRUD views for articles)
2. Categories (Basic model for category selection on an article)
3. Core (Users, Profiles, Channels, Subscriptions and Payouts)
4. Newsletter (Mailchimp newsletter signups)

## Deployment with AWS

This project is hosted using Elastic Beanstalk. Elastic Beanstalk is a Platform As A Service (PaaS) that streamlines the setup, deployment, and maintenance of your app on Amazon AWS. It’s a managed service, coupling the server (EC2), database (RDS), and your static files (S3).

The project's **src** directory contains two required EB directories - **.ebextensions** and **.elasticbeanstalk**

The **.ebextensions** contains a config file with settings for the Django project

The **.elasticbeanstalk** contains a config file specifying settings. The important ones being the default region of the application (us-west-2), the Python version (3.6) and environment ()

To deploy, run the following:

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

Now we need to ssh into the instance so we can run initial commands to setup the server. You can do this using `eb ssh`. When setting up the instance you were probably asked if you'd like to create an ssh key pair. You only need to remember the passphrase for the keypair you created. When using ssh you will be asked to enter the passphrase.

1. Make migrations to the database
2. Create a superuser
3. Collect static files

First activate the virtualenv:

```
source /opt/python/run/venv/bin/activate
```

Navigate to the app

```
cd /opt/python/current/app/
```

To make migrations run

```
python manage.py makemigrations
```

To create the superuser, assuming the virtualenv is activated

```
python manage.py makesuper
```

To collect static files:

```
python manage.py collectstatic --noinput
```

If there are changes to the projects models and you need to makemigrations, you will need to run `eb deploy` with the new code and then handle migrations on the server
