import base64
import datetime
import re
from datetime                                       import datetime as dt
from django.utils                                   import timezone
from django.utils.translation                       import gettext_lazy as _
from django.conf                                    import settings
from cryptography.fernet                            import Fernet



def encrypt(text):
    """ https://morioh.com/p/4f5288b77c14 """
    try:
        text = str(text) # convert integer etc to string first
        cipher_suite = Fernet(settings.FERNET_KEY) # get the key from settings, key should be byte
        encrypted_text = cipher_suite.encrypt(text.encode('ascii')) # input should be byte, so convert the text to byte
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode('ascii') # encode to urlsafe base64 format
        return encrypted_text
    except Exception as e:
        return None


def decrypt(text):
    """ https://morioh.com/p/4f5288b77c14 """
    try:
        text = base64.urlsafe_b64decode(text) # base64 decode
        cipher_suite = Fernet(settings.FERNET_KEY) # get the key from settings, key should be byte
        decoded_text = cipher_suite.decrypt(text).decode('ascii') # decrypt and decode
        return decoded_text
    except Exception as e:
        return None


def format_display_date(date):
    """ Convert string to date format `Mon, 01/01/20`. """
    try:
        date = dt.strptime(date, '%Y-%m-%d')
    except:
        date = None
    if not date: return
    return date.strftime('%a, %d/%m/%y')


def parse_ocr_date(date):
    """ Parse date from OCR response `dd-mm-yyyy` to date object. """
    if not date: return
    return dt.strptime(date, '%d/%m/%Y')


def calculate_age(date):
    """
    Calculate age based on passed date and date now.
    Passed date format needs to be `yyyy-mm-dd`.
    """
    if not date or not isinstance(date, datetime.date): return 0
    today = timezone.now()
    return today.year - date.year - ((today.month, today.day) < (date.month, date.day))


def generate_arrival_time():
    """ Generate array of time with interval 30 sec. """
    result = []
    loop = dt.strptime('00:00', '%H:%M')
    end = dt.strptime('23:59', '%H:%M')
    while(loop < end):
        result.append((dt.strftime(loop, '%H:%M'), '%s - %s' % (dt.strftime(loop, '%H:%M'), dt.strftime(loop + datetime.timedelta(minutes=30), '%H:%M'))))
        loop += datetime.timedelta(minutes=30)
    return result


def parse_arrival_time(time):
    """ Convert string to time format `00:00`. """
    try:
        time = dt.strptime(time, '%H:%M:%S')
    except:
        time = dt.strptime('14:00', '%H:%M')
    return time.strftime('%H:%M')


def replace_symbols(text):

    text = re.sub('[^a-zA-Z0-9 ]', '', text)
    text = re.sub('\s', '_', text)
    return text


def get_properties(property_id):

    data = {}
    if not property_id:
        return data
    
