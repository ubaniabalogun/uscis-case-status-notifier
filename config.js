const prompt = require('cli-prompt')
const AWS = require('aws-sdk')
const package = require('./package.json')

// Collect environment variables for Lambda Function and Upload them to SSM

let prompt_questions = [
  {
    key: 'uscisReceiptNum',
    label: 'USCIS Case Receipt Number'
  },
  {
    key: 'twilioAccountSid',
    label: 'Twilio Account SID'
  },
  {
    key: 'twilioAuthToken',
    type: 'password',
    label: 'Twilio Auth Token'
  },
  {
    key: 'twilioNumber',
    label: 'Twilio Phone Number (include country code)',
  },
  {
    key: 'recipientNumber',
    label: 'Recipient Number (include country code)'
  }
]

prompt.multi(prompt_questions, function(results) {
  let envVariables = [
    {
      Name: '/twilio/account_sid',
      Type: 'SecureString',
      Value: results.twilioAccountSid,
      Description: 'Twilio Account SID',
      Overwrite: true
    },
    {
      Name: '/twilio/auth_token',
      Type: 'SecureString',
      Value: results.twilioAuthToken,
      'Description': "Twilio Auth Token",
      Overwrite: true
    },
    {
      Name: '/twilio/phonenumber',
      Type: 'SecureString',
      Value: results.twilioNumber,
      Description: 'Twilio Phone Number',
      Overwrite: true
    },
    {
      Name: '/uscis/receipt_number',
      Type: 'SecureString',
      Value: results.uscisReceiptNum,
      Description: 'USCIS Case Receipt Number',
      Overwrite: true
    },
    {
      Name: '/uscis/recipient_number',
      Type: 'SecureString',
      Value: results.recipientNumber,
      Description: "Recipient's Number",
      Overwrite: true
    }
  ]

  const awsCreds = new AWS.SharedIniFileCredentials({profile: package.config.awsProfile })
  const ssm = new AWS.SSM({credentials: awsCreds , region: package.config.region })

  envVariables.forEach( function(variable) {
    ssm.putParameter(variable, (err, data) => {
      if (err) {
        console.log(err, err.stack)
      }else {
        console.log(`Uploaded ${variable.Description} to AWS SSM Parameter Store`)
      }
    })
  })
  
  console.log("uscis-case-status-notifier is ready to deploy.")
},
console.error
)
