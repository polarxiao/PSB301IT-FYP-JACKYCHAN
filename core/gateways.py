import requests, json
from json                       import JSONDecodeError
from django.conf                import settings
from django.utils.translation   import ugettext as _

    
# ocr scanning
def ocr(image_file):
    url = settings.OCR_ENDPOINT_URL
    files = {'image': open(image_file, 'rb')}
    data, headers = {}, {'x-api-key': settings.OCR_ENDPOINT_KEY}
    data['selectionCode'] = ['']
    data['skipFaceDetect'] = ['']
    try:
        response = requests.post(url, files=files, data=data, headers=headers, timeout=settings.OCR_ENDPOINT_TIMEOUT_LIMIT)
        response.raise_for_status()
        json_response = json.loads(response.content.decode('utf-8'))
    except requests.exceptions.HTTPError as http_error:
        try:
            json_response = json.loads(response.content.decode('utf-8'))
        except JSONDecodeError:
            json_response = {'status': 'error', 'message': response.content.decode('utf-8')}
    except requests.exceptions.RequestException as request_error:
        json_response = {'status': 'error', 'message': _('Error connecting to server')}
    return json_response

# fr compare
def fr_endpoint(image1, image2):
    url = settings.FR_ENDPOINT_URL
    params = {'api_key': settings.FR_API_KEY, 'api_secret': settings.FR_API_SECRET}
    files = {'image_file1': open(image1, 'rb'),  'image_file2': open(image2, 'rb')}
    try:
        response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        json_response = json.loads(response.content.decode('utf-8'))
    except requests.exceptions.HTTPError as http_error:
        try:
            json_response = json.loads(response.content.decode('utf-8'))
        except json.JSONDecodeError:
            json_response = {'status': 'error', 'message': response.content.decode('utf-8')}
    except requests.exceptions.RequestException as request_error:
        json_response = {'status': 'error', 'message': _('Error connecting to server')}
    return json_response

