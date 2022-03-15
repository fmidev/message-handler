import json
import urllib.request
from convert_version import *

def process_notification(req, hdrs, m_callback, e_callback):
    print(f"Processing notification from sns queue '{hdrs.get('X-Amz-Sns-Topic-Arn')}'")

    msg = json.loads(req['Message'])
    msg = convert_to_2021_05_27(msg)

    if (m_callback is not None and m_callback(msg)) or m_callback is None:
        e_callback(msg)


def process_subscription(req, hdrs):
    print("Processing subscription confirmation for topic {} by reading url {}".format(hdrs.get('X-Amz-Sns-Topic-Arn'), req['SubscribeURL']))
    print(urllib.request.urlopen(req['SubscribeURL']).read())


def handle(req, hdrs, m_callback, e_callback):
    """handle a request to the function
    Args:
        req (str): request body
    """

    jreq = None

    try:
        jreq = json.loads(req)
    except json.decoder.JSONDecodeError as e:
        print("Input not valid json")
        return 'OK'

    try:
        amz_type = hdrs.get("X-Amz-Sns-Message-Type")

        if amz_type == "Notification":
            msg = None
            try:
                msg = jreq["Records"][0]["Sns"]
            except KeyError as e:
                msg = jreq

            process_notification(msg, hdrs, m_callback, e_callback)
        elif amz_type == "SubscriptionConfirmation":
            process_subscription(jreq, hdrs)
        else:
            print(f"Unsupported x_amz_sns_message_type: {amz_type}")

    except KeyError as e:
        print(f"KeyError for {e}")

    return 'OK'

