# runtime python 3.6
import json
import logging
import os
import re
import botocore.vendored.requests as requests
import boto3
import datetime

HOOK_URL = os.environ['WebhookUrl']
MESSENGER = os.environ['Messenger']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    now = datetime.datetime.now()+ datetime.timedelta(hours=5, minutes=30)
    Indian_time = now.strftime('%Y-%b-%d %l:%M:%S %p')
    # start logging
    # logger.info("Event: " + str(event))

    # message = json.loads(event['Records'][0]['Sns']['Message'])
    # message = json.loads(event)
    message = event
    logger.info("Message: " + str(message))

    # use data from logs
    pipeline = message['detail']['pipeline']
    # awsAccountId = message['account']
    awsRegion = message['region']
    eventTime = message['time']
    # stage = message['detail']['stage']
    state = message['detail']['state']
    # action = message['detail']['action']
    # category = message['detail']['type']['category']
    # set the color depending on state/category for Approval
    color = "Attention"
    # if action == 'Approval':
    #    color = "#ff9000"
    if state == 'SUCCEEDED':
        color = "#00ff00"
    elif state == 'STARTED':
        color = "#00bbff"
    elif state == 'FAILED':
        color = "#ff0000"

    # data for message cards

    if pipeline == 'Webhook-Pipeline':
        title = "ETL Deployment"
    # title = pipeline
    # accountString = "Account"
    regionString = "Region"
    timeString1 = "Event time (UTC) "
    timeString = "Event time (Local)"
    # stageString = "Stage"
    stateString = "State"
    # actionString = "Action"
    dateString = re.split('T|Z', eventTime)
    dateString = f'{dateString[0]} {dateString[1]}'
    # pipelineURL = f"https://{awsRegion}.console.aws.amazon.com/codesuite/codepipeline/pipelines/{pipeline}/view?region={awsRegion}"
    if pipeline == 'Webhook-Pipeline':
        pipelineURL = f'https://google.com'
    #image for message card
    if state == 'SUCCEEDED':
        image = f'https://www.letstalk.net.in/success1.gif'
    elif state == 'STARTED':
        image = f'https://www.letstalk.net.in/start4.gif'
    elif state == 'FAILED':
        image = f'https://www.letstalk.net.in/besterror1.gif'
    
    # MS Teams data
    MSTeams = {
        "title": "%s" % title,
        "info": [
            {"activityImage": image, "size": "medium"},
            {"facts":
                [  # { "name": accountString, "value": awsAccountId },
                     {"name": regionString, "value": awsRegion},
                    # {"name": timeString1, "value": dateString},
                    { "name": timeString, "value": Indian_time},
                    # { "name": actionString, "value": action },
                     {"name": stateString, "value": state}
                    ], "color": "00ff00"}
       
        ],
       
        "link": [
            {"@type": "OpenUri", "name": "Open Web Link", "targets":
                [
                    {"os": "default", "uri": pipelineURL}
                ]
             }
        ]
    }
   

    # build MS Teams message
    if MESSENGER == "msteams":
        message_data = {
            "summary": "summary",
            "$schema": "https://schema.org/extensions",
            "@type": "MessageCard",
            "themeColor": "#808080",
            "color": color,
            "title": MSTeams["title"],
            "sections": MSTeams["info"],
            "potentialAction": MSTeams["link"],
        }

    # send message to webhook
    requests.post(HOOK_URL, json.dumps(message_data))
    
