"""
Checks the status of a USCIS Case using its receipt number
"""
import requests, os, boto3
from bs4 import BeautifulSoup, SoupStrainer
from twilio.rest import Client


USCIS_CASE_STATUS_PAGE = "https://egov.uscis.gov/casestatus/mycasestatus.do"
CASE_STATUS_TABLE = os.environ['CASE_STATUS_TABLE']
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_PHONE_NUMBER = os.environ['TWILIO_PHONE_NUMBER']
RECIPIENT_NUMBER = os.environ['RECIPIENT_NUMBER']
RECEIPT_NUMBER = os.environ['RECEIPT_NUMBER']

class Case:
    """Represents a USCIS case and the actions that can be taken on it
    """

    def __init__(self, receipt_number):
        """Initializes the Case object
        Args:
            receipt_number (string): USCIS receipt number
        """
        self.receipt_number = receipt_number

    @property
    def current_status(self):
        """Current status of the case from the USCIS website
        """
        data = {'initCaseSearch': 'CHECK STATUS', 'appReceiptNum': self.receipt_number}
        r = requests.post(USCIS_CASE_STATUS_PAGE, data=data)
        status_soup = BeautifulSoup(r.content, 'html.parser', parse_only=SoupStrainer('h1'))
        status = status_soup.string
        if not status:
            raise Exception("No status was found for the given receipt_number on the USCIS website. receipt_number may be invalid or site html may have changed.")
        return status

    @property
    def last_known_status(self):
        """Last known status of the case stored in the backend DB
        """
        statuses_table = boto3.resource('dynamodb').Table(CASE_STATUS_TABLE)
        item = statuses_table.get_item(Key={'receipt_number': self.receipt_number}).get('Item',{})
        if not item:
            raise KeyError('The provided receipt_number does not exist in the backend case statuses table.')
        status = item.get('last_known_status','')
        return status


    @last_known_status.setter
    def last_known_status(self, status):
        """Update the last known status of the case in the backend DB
        Args:
            status (string): The new status to set
        """
        statuses_table = boto3.resource('dynamodb').Table(CASE_STATUS_TABLE)
        statuses_table.put_item(Item={
        'receipt_number': self.receipt_number,
        'last_known_status': status
        })


def send_status_change_notification(phone_number, current_status):
    """Sends an SMS with a status change update
    Args:
        phone_number: The phone number to text the status change to
        current_status: The current status of the USCIS case number
    Returns:
        string: The message sid of the sent message
    """
    STATUS_UPDATE_MSG = "Hey! Your USCIS case status has been updated. The current status is \"{}\"".format(current_status)
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = twilio_client.messages.create(
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number,
        body=STATUS_UPDATE_MSG
    )
    return message.sid


def lambda_handler(event, context):
    """AWS Lambda entry point

    Args:
        event (dict): Event details
        context (obj): AWS Lambda context object
    """
    uscis_case = Case(RECEIPT_NUMBER)
    current_status = uscis_case.current_status
    last_known_status = uscis_case.last_known_status

    if current_status != last_known_status:
        send_status_change_notification(RECIPIENT_NUMBER, current_status)
        uscis_case.last_known_status = current_status
        print("SENT_UPDATE")
        return 'SENT_UPDATE'
    else:
        print("NO_UPDATE")
        return 'NO_UPDATE'
