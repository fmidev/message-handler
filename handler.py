import json
import urllib.request


def process_notification(req, hdrs, m_callback, e_callback):
    print(f"Processing notification from sns queue '{hdrs.get('X-Amz-Sns-Topic-Arn')}'")

    msg = json.loads(req['Message'])

    if (m_callback is not None and m_callback(msg)) or m_callback is None:
        e_callback(msg)


def process_subscription(req, hdrs):
    print(f"Processing subscription confirmation for topic {hdrs.get('X-Amz-Sns-Topic-Arn')}")
    urllib.request.urlopen(req['SubscribeURL']).read()


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
            process_notification(jreq["Records"][0]["Sns"], hdrs, m_callback, e_callback)
        elif amz_type == "SubscriptionConfirmation":
            process_subscription(jreq, hdrs)
        else:
            print(f"Unsupported x_amz_sns_message_type: {amz_type}")

    except KeyError as e:
        print(f"KeyError for {e}")

    return 'OK'

