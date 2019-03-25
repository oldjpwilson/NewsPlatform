# NewsPlatform

Notes on the project

## Workflow

When making a change to the project we need to test it before pushing it live. This is the workflow for that:

1. Change into the test branch (already created for you)
2. Pull the latest version of the master branch
3. Make the change you want to implement
4. Change the _manage.py_ file to use **newsPlatform.settings.test** file (Important)
5. Change the _wsgi.py_ file to use **newsPlatform.settings.test** (Important)
6. Change the elasticbeanstalk _config.yml_ file to use the **test** environment (Important)
7. Change the ebextensions _django.config_ file to use **newsPlatform.settings.test** (Important)
8. Commit the changes to the test branch
9. Deploy the changes to the AWS test environment (already created for you) ['eb deploy']
10. See if the change works
11. Change the _manage.py_, _wsgi.py_ and _django.config_ files back to use **newsPlatform.settings.production** (Important)
12. Change the elasticbeanstalk _config.yml_ file back to use the **prod** environment (Important)
13. Commit the changes to the test branch
14. Push the changes to the test branch
15. Merge the test branch into the master branch
16. Deploy the now updated project to the AWS prod enviroment

## Something important to know about when deploying for the first time to a new environment

In the django.config file are a list of commands to execute after every deployment. For some reason the first deployment fails on the second command. I believe this is because the code needs to be deployed on its own before any commands are included. So to get around this issue, for the first deployment, remove the commands from the config file (commit, push to git) and the deploy. That deployment is basically just deploying the code. Then add the commands back to the config file (commit, push to git) and deploy again. This time the commands will be executed with no problem because the code is definitely there.

## Development

1. Install dependencies with `pip install -r requirements.txt`
2. Run migrations with `python manage.py migrate`

In this repository, the dev branch is used for working on localhost. To run the server for development use: `python manage.py runserver --settings=newsPlatform.settings.development`. The admin user password is `newsplatform`.

**IMPORTANT** - when working in development it's important to use the settings argument: `--settings=newsPlatform.settings.development` in every `python manage.py` command.

## Settings

There are four settings in the projects root folder: **newsPlatform**. One for base settings. One for development (localhost), one for testing purposes (live) and one for production (live)

## Apps

There are currently four apps:

1. Articles (CRUD views for articles)
2. Categories (Basic model for category selection on an article)
3. Core (Users, Profiles, Channels, Subscriptions and Payouts)
4. Newsletter (Mailchimp newsletter signups)

## Deployment with AWS

This project is hosted using Elastic Beanstalk. Elastic Beanstalk is a Platform As A Service (PaaS) that streamlines the setup, deployment, and maintenance of your app on Amazon AWS. It’s a managed service, coupling the server (EC2), database (RDS), and your static files (S3).

The project contains two required EB directories - **.ebextensions** and **.elasticbeanstalk**

The **.ebextensions** contains a config file with settings for the Django project. In the config file the following commands are set to execute on deployment:

1. Make migrations to the database
2. Create a superuser
3. Create required model instances
4. Collect static files

The **.elasticbeanstalk** contains a config file specifying settings. The important ones are the default region of the application (us-west-2), the Python version (3.6) and environment (prod or test)

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

DNS records were changed from the domain account manager to AWS and can be managed in the Route53 console. This also means the email host provider (Domain.com in this case) has to have an MX Record linked to its DNS so that mails sent to the AWS name servers are rerouted to the email host.

## SSL

[This Namecheap article](https://www.namecheap.com/support/knowledgebase/article.aspx/467/67/how-to-generate-csr-certificate-signing-request-code) provides a very clear article on creating a CSR needed for accessing your SSL. In this case, because I work on a Mac I used the [Apache OpenSSL/ModSSL/Nginx/Heroku](https://www.namecheap.com/support/knowledgebase/article.aspx/9446/14/generating-csr-on-apache--opensslmodsslnginx--heroku) link.

Place the generated SSL files inside the project root directory. In a terminal run the following command to upload the SSL certificate to AWS:

```
aws iam upload-server-certificate --server-certificate-name NewsPlatformCertificate --certificate-body file://newsplatform_org.crt --certificate-chain file://newsplatform_org.ca-bundle --private-key file://server.key
```

Now we need to terminate our load balancer from Http to Https within the configuration settings of our elastic beanstalk environment. Click to _modify_ the Load Balancer and then add a new listener on port 443 with Https that uses our created Certificate. Make sure in the command line you are using the right environment otherwise the certificate will not show up. Use `eb use src-prod --region=us-west-2` to change to our defined environment.

## S3

When in production it's good to make use of S3 for hosting static files. This is good for permissions and access to those files, preventing anyone from scraping your css, js and images. Unexpectedly, web fonts behave weirdly in S3 and hence we needed to add special CORS configuration so that the WYSIWIG editor could have its icons display:

```
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>http://www.newsplatform.org</AllowedOrigin>
    <AllowedOrigin>http://newsplatform.org</AllowedOrigin>
    <AllowedOrigin>https://www.newsplatform.org</AllowedOrigin>
    <AllowedOrigin>https://newsplatform.org</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>HEAD</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
  </CORSRule>
</CORSConfiguration>
```
