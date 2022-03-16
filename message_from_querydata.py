import sys
import newbase
import datetime
import hashlib
from validate import *

def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_timedelta(td):
    s = td.total_seconds()
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

def level_to_string(levelid):
    # qdinfo.cpp: string LevelName(FmiLevelType theLevel)

    if levelid == newbase.kFmiGroundSurface:
        return "GroundSurface"
    elif levelid == newbase.kFmiPressureLevel:
        return "PressureLevel"
    elif levelid == newbase.kFmiMeanSeaLevel:
        return "MeanSeaLevel"
    elif levelid == newbase.kFmiHybridLevel:
        return "HybridLevel"
    elif levelid == newbase.kFmiAltitude:
        return "Altitude"
    elif levelid == newbase.kFmiHeight:
        return "Height"
    elif levelid == newbase.kFmi:
        return "?"
    elif levelid == newbase.kFmiAnyLevelType:
        return "AnyLevelType"
    elif levelid == newbase.kFmiRoadClass1:
        return "RoadClass1"
    elif levelid == newbase.kFmiRoadClass2:
        return "RoadClass2"
    elif levelid == newbase.kFmiRoadClass3:
        return "RoadClass3"
    elif levelid == newbase.kFmiSoundingLevel:
        return "SoundingLevel"
    elif levelid == newbase.kFmiAmdarLevel:
        return "AmdarLevel"
    elif levelid == newbase.kFmiFlightLevel:
        return "FlightLevel"
    elif levelid == newbase.kFmiDepth:
        return "Depth"
    elif levelid == newbase.kFmiNoLevelType:
        return "NoLevel"
    else:
        return "None"



def read_metadata(filename):
    qd = newbase.NFmiQueryData(filename)
    qi = newbase.NFmiFastQueryInfo(newbase.NFmiQueryInfo(qd))

    params = []
    levels = []
    times = []
    producerId = None

    conv = newbase.NFmiEnumConverter()

    qi.Reset()

    while qi.NextParam():
        params.append({ "Name": conv.ToString(qi.Param().GetParam().GetIdent())})
        if producerId is None:
            producerId = qi.Param().GetProducer().GetIdent()

    while qi.NextLevel():
        levels.append({ "Type": level_to_string(qi.Level().LevelType()), "Value": qi.Level().LevelValue() })

    originTime = qi.OriginTime()

    while qi.NextTime():
        step = qi.ValidTime().DifferenceInMinutes(originTime)
        times.append(format_timedelta(datetime.timedelta(minutes=step)))

    originTimeStr = datetime.datetime.strptime(originTime.ToStr(newbase.NFmiString('YYYYMMDDhhmm')).CharPtr(), '%Y%m%d%H%M').strftime('%Y-%m-%dT%H:%M:%S')

    return {
        "params" : params,
        "levels" : levels,
        "times"  : times,
        "origintime" : originTimeStr,
        "producer" : producerId,
        "filename" : filename
    }


def create_message(metadata, run_id, s3bucket, s3endpoint = None, awsregion = None, subproducer = None):

    message = {
      "MessageVersion" : "2021-05-27",
      "MessageTime" : datetime.datetime.utcnow().isoformat(),
      "MessageType" : "DATA_AVAILABLE",
      "DataInfo" :
        {
            "Producer" : { "Id" : str(metadata['producer']), "Namespace" : "radon" },
            "DataSource" : {
               "Name": "S3",
               "S3Info": [{
                 "BucketName": s3bucket,
                 "Files" : [
                   {
                     "FileName" : "{}/{}".format(s3bucket, metadata['filename']),
                     "FileType" : "QUERYDATA",
                     "Md5Sum" : md5(metadata['filename'])
                   }
                 ]
               }]
            },
            "DataType" : "FORECAST",
            "ForecastInfo" : {
              "AnalysisTime" : metadata['origintime'],
              "Parameters" : metadata['params'],
              "Levels" : metadata['levels'],
              "Steps" : metadata['times']
            },
            "RunId" : run_id
        }
    }

    if s3endpoint is not None:
        message['DataInfo']['DataSource']['S3Info'][0]['EndPoint'] = s3endpoint

    if awsregion is not None:
        message['DataInfo']['DataSource']['S3Info'][0]['AwsRegion'] = awsregion

    if subproducer is not None:
        message['DataInfo']['Producer']['SubProducer'] = subproducer

    print(json.dumps(message, indent=4))

    if not validate(message):
        print('Error validating message')
        return None


    return message


def create_message_from_querydata(filename, run_id, s3bucket, subproducer = None):

    metadata = read_metadata(filename)
    return create_message(metadata, run_id, s3bucket, subproducer = subproducer)


if __name__ == "__main__":
    create_message_from_querydata(sys.argv[1], sys.argv[2], sys.argv[3])
