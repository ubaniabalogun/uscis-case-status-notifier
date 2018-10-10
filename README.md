# uscis-case-status-notifier
**What does it do?**

Sends an SMS notification when a USCIS case status changes on the [USCIS website](https://egov.uscis.gov/casestatus/landing.do).

**How does it do it?**

The solution makes use of the following services: AWS Lambda, AWS Cloudwatch, AWS DynamoDB, Twilio API and the USCIS case status website.

An AWS Cloudwatch Event triggers an AWS Lambda function that makes a post request with a USCIS case receipt number to the USCIS case status website. The Lambda function scrapes the returned HTML page for the most current status of the case and compares it with the last status of the case which is stored in DynamoDB.
If the current status of the case differs from the last status, the Lambda function updates DynamoDB with the current status then uses the Twilio API to send an SMS with the current status to the designated number.

## Deployment
The solution is designed to be deployed to AWS using the [Serverless Framework](https://serverless.com).

Ensure the below requirements are handy before deploying:
- An AWS account and API keys for a `serverless-admin` profile
- awscli
- Node.js & npm installed on local system
- USCIS Case Receipt Number
- [Twilio](https://www.twilio.com) Account SID, Auth Token and SMS Capable Phone Number
- Your (or the notification recipient's) phone number

First, execute the below command to configure the service (first-time deploy per only)
```
npm run config
```

The command will prompt you to supply your USCIS Case Receipt Number; Twilio Account SID, Auth Token & Phone Number, and the recipient's phone number. The script will upload this information to AWS SSM Parameter Store to be used by the Lambda Function.

Once the script completes, execute the below command to deploy the service
```
npm run deploy
```

The service deploys to AWS' us-west-2 region by default. You can change the deployment region (or AWS Profile used for deployment), in the `config` variable of the package.json.

To remove the service, execute:
```
npm run remove
```
