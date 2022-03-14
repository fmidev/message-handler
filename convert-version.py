import json
import sys


def convert_2020_03_04_to_2021_05_27(message):
    conv = message.copy()

    try:
        conv['DataInfo']['Producer']['SubProducer'] = message['DataInfo']['DataLabel']
        conv['DataInfo'].pop('DataLabel', None)
    except KeyError as e:
        pass

    conv.pop('MessageCategory', None)

    if conv['DataInfo']['DataSource'] == 'S3':

        s3info = {
            'BucketName': conv['DataInfo']['BucketName'],
            'Files': conv['DataInfo']['Files'],
        }

        try:
            s3info['AwsRegion'] = conv['DataInfo']['AwsRegion']
        except KeyError as e:
            pass

        for i in range(len(s3info['Files'])):
            if 'MD5Sum' in s3info['Files'][i]:
                s3info['Files'][i]['Md5Sum'] = s3info['Files'][i]['MD5Sum']
                s3info['Files'][i].pop('MD5Sum')
        ds = {
            'Name': 'S3',
            'S3Info': [ s3info ]
        }

        conv['DataInfo']['DataSource'] = ds
        conv['DataInfo'].pop('AwsRegion', None)
        conv['DataInfo'].pop('BucketName', None)
        conv['DataInfo'].pop('Files', None)

    elif conv['DataInfo']['DataSource'] == 'radon':
        radon_info = {}

        try:
            radon_info['TableName'] = conv['DataInfo']['TableName']
        except KeyError as e:
            pass

        ds = {
            'Name': 'radon',
            'RadonInfo': radon_info
        }

        conv['DataInfo']['DataSource'] = ds
        conv['DataInfo'].pop('TableName', None)

    try:
        levels = conv['DataInfo']['ForecastInfo']['Levels']
        newlevels = []
        for levtype in levels:
            for levval in levels[levtype]:
                newlevels.append({ 'Type': levtype, 'Value': int(levval) })

        conv['DataInfo']['ForecastInfo']['Levels'] = newlevels
    except KeyError as e:
        pass

    try:
        params = []
        for param in conv['DataInfo']['ForecastInfo']['Parameters']:
            params.append({ 'Name': param })

         
        conv['DataInfo']['ForecastInfo']['Parameters'] = params
    except KeyError as e:
        pass

    conv['MessageVersion'] = '2021-05-27'

    return conv


def convert_to_2021_05_27(message):
    version = message['MessageVersion']

    if version == '2020-03-04':
        return convert_2020_03_04_to_2021_05_27(message)

    raise Exception("Unable to convert from version '{}'".format(version))


if __name__ == "__main__":
    if sys.argv[1] == '-':
        print(json.dumps(convert_to_2021_05_27(json.load(sys.stdin))))
        sys.exit(0)

    with open(sys.argv[1]) as fp:
        message = json.load(fp)
        print(json.dumps(convert_to_2021_05_27(message)))
