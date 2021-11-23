import os
import json
import urllib.request
import pickle

# Need this because openfaas python3 is 3.9 and centos8 has 3.6
pickle.HIGHEST_PROTOCOL = 4
pickle.DEFAULT_PROTOCOL = 4

#from rq import Queue
#from redis import Redis

#def get_queue_name(msg):
#    ds = msg['DataInfo']['DataSource']
#    if ds == "S3":
#        return "ingest"
#    elif ds == "radon":
#        mtype = msg['MessageType']
#        if mtype == 'DATA_AVAILABLE':
#            return "process"
#        elif mtype == 'FULL_FORECAST_AVAILABLE':
#            return "convert"
#
#    return None

#def push_to_redis(msg):
#    redis_conn = Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"])

#    qname = get_queue_name(msg)

#    if qname is None:
#        print("No queue defined for this type of message")
#        return

#    q = Queue(qname, connection=redis_conn)

#    job = None
#    if qname == "ingest":
#        job = q.enqueue('parse_and_load.process_notification', json.dumps(msg))
#    elif qname == "process" or qname == "convert":
#        job = q.enqueue('parse_and_process.process_notification', json.dumps(msg))

#    print(f"Enqueued job {job} to queue {qname}")


def process_notification(req):
    print(f"Processing notification from {os.environ['Http_X_Amz_Sns_Topic_Arn']}")
    msg = json.loads(req['Message'])

    producer = msg['DataInfo']['Producer']

    if producer['Namespace'] == 'ECMWF':
        print(msg)
#        push_to_redis(msg)
    elif producer['Namespace'] == 'radon' and producer['Id'] in ('131','134','242'):
        print(msg)
#        push_to_redis(msg)
    else:
        print(f"Got uninteresting message concerning {producer['Namespace']}/{producer['Id']}")


def process_subscription(req):
    print(f"Processing subscription confirmation for topic {os.environ['Http_X_Amz_Sns_Topic_Arn']}")
    urllib.request.urlopen(req['SubscribeURL']).read()


def handle(req):
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
        # http headers are environment variables in openfaas functions
        # https://github.com/openfaas/workshop/blob/master/lab4.md#inject-configuration-through-environmental-variables
        amz_type = os.environ["Http_X_Amz_Sns_Message_Type"]

        if amz_type == "Notification":
            process_notification(jreq)
        elif amz_type == "SubscriptionConfirmation":
            process_subscription(jreq)
        else:
            print(f"Unsupported x_amz_sns_message_type: {amz_type}")

    except KeyError as e:
        print(f"KeyError for {e}")

    return 'OK'

