import base64
import hashlib
import hmac
import uuid
import json
import mimetypes

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

AWS_MAX_SIZE = 15000000000

import boto
from boto.s3.connection import Key, S3Connection


@csrf_exempt
def success_redirect_endpoint(request):
    """ This is where the upload will snd a POST request after the
    file has been stored in S3.
    """

    if request.method == "POST":
        bucket_name = request.POST.get('bucket')
        key_name = request.POST.get('key')
        cloud_front = getattr(settings, 'AWS_CLOUDFRONT_DOMAIN', None)
        temp_link = "https://%s.s3.amazonaws.com/%s" % (bucket_name, key_name)
        if cloud_front:
            temp_link = "https://%s/%s" % (cloud_front, key_name)
        content = {
            "tempLink": temp_link
        }
        return make_response(200, json.dumps(content))
    else:
        return make_response(405)


def handle_POST(request):
    """ Handle S3 uploader POST requests here. For files <=5MiB this is a simple
    request to sign the policy document. For files >5MiB this is a request
    to sign the headers to start a multipart encoded request.
    """
    if request.POST.get('success', None):
        return make_response(200)
    else:
        request_payload = json.loads(request.body)
        headers = request_payload.get('headers', None)
        if headers:
            # The presence of the 'headers' property in the request payload
            # means this is a request to sign a REST/multipart request
            # and NOT a policy document
            response_data = sign_headers(headers)
        else:
            if not is_valid_policy(request_payload):
                return make_response(400, {'invalid': True})
            response_data = sign_policy_document(request_payload)
        response_payload = json.dumps(response_data)
        return make_response(200, response_payload)


def handle_DELETE(request):
    """ Handle file deletion requests. For this, we use the Amazon Python SDK,
    boto.
    """
    try:

        boto.set_stream_logger('boto')
        S3 = S3Connection(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    except ImportError as e:
        print("Could not import boto, the Amazon SDK for Python.")
        print("Deleting files will not work.")
        print("Install boto with")
        print("$ pip install boto")

    if boto:
        bucket_name = request.POST.get('bucket')
        key_name = request.POST.get('key')
        try:
            aws_bucket = S3.get_bucket(bucket_name, validate=False)
            aws_key = Key(aws_bucket, key_name)
            aws_key.delete()
            return make_response(200)
        except Exception as err:
            print(err)
            return make_response(500)
    else:
        return make_response(500)


def make_response(status=200, content=None):
    """ Construct an HTTP response. Fine Uploader expects 'application/json'.
    """
    response = HttpResponse()
    response.status_code = status
    response['Content-Type'] = "application/json"
    response.content = content
    return response


def is_valid_policy(policy_document):
    """ Verify the policy document has not been tampered with client-side
    before sending it off.
    """
    # bucket = settings.AWS_STORAGE_BUCKET_NAME
    # parsed_max_size = settings.AWS_MAX_SIZE
    bucket = ''
    parsed_max_size = 0
    for condition in policy_document['conditions']:
        if isinstance(condition, list) and condition[0] == 'content-length-range':
            parsed_max_size = condition[2]
        else:
            if condition.get('bucket', None):
                bucket = condition['bucket']
    return bucket == settings.AWS_STORAGE_BUCKET_NAME and int(parsed_max_size) == AWS_MAX_SIZE


def sign_policy_document(policy_document):
    """ Sign and return the policy doucument for a simple upload.
    http://aws.amazon.com/articles/1434/#signyours3postform
    """
    policy = base64.b64encode(json.dumps(policy_document))
    signature = base64.b64encode(hmac.new(settings.AWS_SECRET_ACCESS_KEY, policy, hashlib.sha1).digest())
    return {
        'policy': policy,
        'signature': signature
    }


def sign_headers(headers):
    """ Sign and return the headers for a chunked upload. """
    return {
        'signature': base64.b64encode(hmac.new(settings.AWS_SECRET_ACCESS_KEY, headers, hashlib.sha1).digest())
    }


@permission_classes((IsAuthenticated,))
def sign_s3_upload(request):
    object_name = request.GET['objectName']
    folder_name = request.GET["folderName"]
    object_name = str(uuid.uuid4()) + "-" + object_name
    key_name = folder_name + "/" + object_name
    content_type = request.GET.get("contentType", mimetypes.guess_type(object_name)[0])
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    import boto3
    from botocore.client import Config

    # Get the service client with sigv4 configured
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, config=Config(signature_version='s3v4'))


    # Generate the URL to get 'key-name' from 'bucket-name'
    signed_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': bucket_name,
            'Key': key_name,
            'ACL': 'public-read',
            'ContentType': content_type
        }
    )

    cloud_front = getattr(settings, 'AWS_CLOUDFRONT_DOMAIN', None)
    cloud_front_url = "https://%s.s3.amazonaws.com/%s" % (bucket_name, key_name)
    if cloud_front:
        cloud_front_url = "https://%s/%s" % (cloud_front, key_name)
    response = {
        'signedUrl': signed_url,
        'cloudFrontURL': cloud_front_url
    }
    return HttpResponse(json.dumps(response))
