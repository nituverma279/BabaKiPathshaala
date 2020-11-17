from geniusapp import app
import boto3
from botocore.exceptions import ClientError

app.config["S3_KEY"] =  'AKIA42EFYJ6Y5AMUMERX' 
app.config["S3_SECRET"] = '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'
app.config['AWS_REGION']='ap-south-1'

def send_email(subject,message,receipent_email_arr):
     
    SENDER = "Geniusedu <support@geniusedu.my>"
    TOADDRESSES = receipent_email_arr
    SUBJECT = subject
    BODY_HTML = message
    CHARSET = "UTF-8"
    client = boto3.client('pinpoint-email', aws_access_key_id=app.config["S3_KEY"],aws_secret_access_key=app.config["S3_SECRET"],region_name= app.config['AWS_REGION'])

    # Send the email.
    try:
         
        response = client.send_email(
            FromEmailAddress=SENDER,
            Destination={
                'ToAddresses': TOADDRESSES,
            },
            Content={
                'Simple': {
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML
                        },
                    }
                }
            },
        )
     
    except Exception as e:
        return 'fail'
    else:
        return 'sent'