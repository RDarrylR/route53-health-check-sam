from aws_lambda_powertools import Logger, Tracer, Metrics
import boto3
import requests
import json
import os
import traceback

logger = Logger(service="HealthCheck-Status-Changed")
tracer = Tracer(service="HealthCheck-Status-Changed")
metrics = Metrics(namespace="HealthCheck", service="HealthCheck-Status")


@tracer.capture_method
def send_slack_message(payload, webhook):
    logger.debug(f"payload={payload}\nwebhook={webhook}")
    
    headers = {'Content-Type': 'application/json'}
    return requests.post(webhook, data=json.dumps(payload), headers=headers)
    

@tracer.capture_method
def publish_to_sns(subject, message, topic):
    logger.debug(f"subject={subject} message={message} topic={topic}")
    # Send message to SNS
    sns_client = boto3.client('sns')
    response = sns_client.publish(TopicArn=topic, Subject=subject, Message=message)
    logger.info(response)


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):

    SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
    SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
    
    logger.info(event)
    
    logger.info(f"SNS_TOPIC_NAME={SNS_TOPIC_ARN}")
    logger.info(f"SLACK_WEBHOOK_URL={SLACK_WEBHOOK_URL}")
    try:                
        if event['detail-type'] != "CloudWatch Alarm State Change":
            logger.error(f"This is not an event we care about - not sure why we got here")
            return
        
        event_detail = event['detail']
        site_that_changed = event_detail['alarmName'][:event_detail['alarmName'].find('-HealthCheckAlarm')]
        logger.info(f"site_that_changed={site_that_changed}")
        new_status = event_detail['state']['value']
        logger.info(f"new_status={new_status}")    
        
        if new_status != 'OK':
            icon = ":x:"
            text_status = "DOWN"
        else:
            icon = ":white_check_mark:"
            text_status = "UP"
            
        message_to_show = f"{icon} {site_that_changed} ( https://{site_that_changed} ) is now {text_status}"    
        slack_data = {
            "text": message_to_show
        }         
        
        if SLACK_WEBHOOK_URL:    
            logger.info(f"slack_data={slack_data}")
            slack_response = send_slack_message(slack_data, SLACK_WEBHOOK_URL)
            logger.info(f"slack_response={slack_response}")         
                    
        sns_subject = f"{site_that_changed} is now {text_status}"
        sns_msg = f"https://{site_that_changed} is now {text_status}"
        sns_response = publish_to_sns(sns_subject, sns_msg, SNS_TOPIC_ARN)
        logger.info(f"sns_response={sns_response}") 
        
    except:
        traceback.print_exc()
        logger.info(f"traceback={traceback.format_exc()}")

