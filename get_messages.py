# coding:utf-8

import logging
import requests
import wikipedia
import traceback
import json
import os
from doco.client import Client


log_level = os.environ.get('LOG_LEVEL', 'INFO')

logger = logging.getLogger()

if log_level == 'ERROR':
    logger.setLevel(logging.ERROR)
elif log_level == 'DEBUG':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


def docomo_response(text):
    docomo_client = Client(
        apikey=os.environ['DOCOMO_API_KEY']
    )
    response = docomo_client.send(utt=text, apiname='Dialogue')

    logger.debug(response)

    return [
        {
        "type":"text",
        "text": response['utt']
        }
    ]


def wikipedia_search(text):
    wikipedia.set_lang('ja')
    index = text.find('って何')
    search_text = text[0:index]
    search_response = wikipedia.search(search_text)

    logger.debug(search_response)

    if len(search_response) > 0:
        logger.debug(len(search_response))
        logger.debug('search_response[0]:' + search_response[0])

        try:
            wiki_page = wikipedia.page(search_response[0])
        except Exception as e:
            try:
                wiki_page = wikipedia.page(search_response[1])
            except Exception as e:
                logger.error(traceback.format_exc())

        response_string = '説明します\n'
        response_string += wiki_page.content[0:200] + '.....\n'
        response_string += wiki_page.url
    else:
        response_string = '今はまだ見つけられませんでした。'

    logger.debug(response_string)

    return [
        {
        "type":"text",
        "text": response_string
        }
    ]


def weather_information(text):
    weather_api_url = 'http://weather.livedoor.com/forecast/webservice/json/v1'
    response_string = ''
    city_id = '270000'

    try:
        params = {'city':city_id}
        response = requests.get(weather_api_url,params=params)

        logger.debug(response)

        response_dict = json.loads(response.text)

        logger.debug(response_dict)

        title = response_dict["title"]
        description = response_dict["description"]["text"]
        response_string += title + "です。\n\n"
        forecasts_array = response_dict["forecasts"]
        forcast_array = []

        logger.debug(response_string)

        for forcast in forecasts_array:
            telop = forcast["telop"]
            temperature = forcast["temperature"]
            min_temp = temperature["min"]
            max_temp = temperature["max"]
            temp_text = ''

            if min_temp is not None:
                if len(min_temp) > 0:
                    temp_text += '\n最低気温は' + min_temp["celsius"] + "度です。"
            if max_temp is not None:
                if len(max_temp) > 0:
                    temp_text += '\n最高気温は' + max_temp["celsius"] + "度です。"

            forcast_array.append(forcast["dateLabel"] + ' ' + telop + temp_text)
        if len(forcast_array) > 0:
            response_string += '\n\n'.join(forcast_array)
        response_string += '\n\n' + description

        logger.debug(response_string)

    except Exception as e:
        logger.error(traceback.format_exc())
        response_string = 'すいません。天気検索でエラーを起こしてしまいました。'

    logger.debug(response_string)

    return [
        {
            "type": "text",
            "text": response_string
        }
    ]


def information():
    return [
        {
            "type": "template",
            "altText": u"お得情報",
            "template": {
                "type": "carousel",
                "columns": [
                    {
                        "thumbnailImageUrl": "https://s3-ap-northeast-1.amazonaws.com/demo.denki.science/mineo-inf.jpg",
                        "title": u"iPhone SE SIMフリー mineoにしてみました",
                        "text": u"SIMの見直しでこんなにもお得",
                        "actions": [
                            {
                                "type": "uri",
                                "label": u"詳細を見る",
                                "uri": "http://www.yamamanx.com/iphone-se-sim-free-mineo/"
                            }
                        ]
                    },
                    {
                        "thumbnailImageUrl": "https://s3-ap-northeast-1.amazonaws.com/demo.denki.science/mineo-top.jpg",
                        "title": u"mineo紹介キャンペーン",
                        "text": u"Amazonギフト券2,000円をプレゼント",
                        "actions": [
                            {
                                "type": "uri",
                                "label": u"申込みページ",
                                "uri": "http://mineo.jp/syokai/?jrp=syokai&kyb=T3G8C9Y2H6"
                            }
                        ]
                    },
                ]
            }
        }
    ]