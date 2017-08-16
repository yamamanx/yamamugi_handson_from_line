# coding:utf-8

import logging
import traceback
import requests
import json
import boto3
import os
import get_messages


log_level = os.environ.get('LOG_LEVEL', 'INFO')

logger = logging.getLogger()

if log_level == 'ERROR':
    logger.setLevel(logging.ERROR)
elif log_level == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

LINE_BOT_API_REPLY = 'https://api.line.me/v2/bot/message/reply'

LINE_HEADERS = {
    'Content-type': 'application/json; charset=UTF-8',
    'Authorization':'Bearer {channel_access_token}'.format(
        channel_access_token=os.environ['LINE_TOKEN']
    )
}


def lambda_handler(event, context):

    try:
        logger.debug(event)
        msg = event['events'][0]
        text = msg['message']['text']
        reply_token = msg['replyToken']
        chat_type = msg['source']['type']
        if chat_type == 'user':
            line_code = msg['source']['userId']
        elif chat_type == 'room':
            line_code = msg['source']['roomId']
        else:
            line_code = ''

        logger.debug(msg)
        logger.debug(text)
        logger.debug(reply_token)
        logger.debug(chat_type)
        logger.debug(line_code)

        if text.find('得') > -1 or text.find('節') > -1 or  text.find('金') > -1:
            messages = get_messages.information()
        elif text.find('天気') > -1 or text.find('雨') > -1 or  text.find('雪') > -1 or text.find('晴') > -1:
            messages = get_messages.weather_information(text)
        elif text.find('って何') > -1:
            messages = get_messages.wikipedia_search(text)
        else:
            messages = get_messages.docomo_response(text)

        logger.debug(messages)

        payload = {
            "replyToken": reply_token,
            "messages": messages
        }

        logger.debug(payload)

        post_response = requests.post(
            LINE_BOT_API_REPLY,
            headers=LINE_HEADERS,
            data=json.dumps(payload)
        )

        logger.debug(post_response.text)

        response_event = {
            'line_code': line_code,
            'text': text,
            'reply': messages[0].get('text','information')
        }

        logger.debug(response_event)

        client = boto3.client('stepfunctions')
        client.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps(response_event)
        )

        return response_event

    except Exception as e:
        logger.error(traceback.format_exc())
        raise(traceback.format_exc())