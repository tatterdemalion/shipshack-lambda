import urllib
import boto3
from botocore.client import Config
from wand.image import Image

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))


def resize_image(image, resize_width, resize_height):
    original_ratio = image.width / float(image.height)
    resize_ratio = resize_width / float(resize_height)

    if original_ratio > resize_ratio:
        resize_height = int(round(resize_width / original_ratio))
    else:
        resize_width = int(round(resize_height * original_ratio))
    if ((image.width - resize_width) + (image.height - resize_height)) < 0:
        filter_name = 'mitchell'
    else:
        filter_name = 'lanczos2'
    image.resize(width=resize_width, height=resize_height,
                 filter=filter_name, blur=1)
    return image


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))
    response = s3.get_object(Bucket=bucket, Key=key)
    with Image(blob=response['Body'].read()) as image:
        resized_data = resize_image(image, 400, 400).make_blob()
    s3.put_object(Bucket='shipshack-thumbnails', Key=key,
                  Body=resized_data,
                  ContentType=response['ContentType'])
    return response['ContentType']
