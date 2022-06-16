import os
import base64
from datetime                   import datetime as dt
from django                     import forms
from django.conf                import settings
from django.utils.translation   import gettext, gettext_lazy as _
from requests                   import request
from core                       import fields, gateways


class CheckInLoginForm(forms.Form):
    reservation_no  = forms.CharField(label=_('Reservation Number'), required=False)
    check_in_date   = forms.DateField(label=_('Check-in Date'), required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''
        self.response = {}
        self.fields['reservation_no'].initial = self.request.session.get('check_in', {}).get('preload', {}).get('reservation_no')
        self.fields['check_in_date'].initial = self.request.session.get('check_in', {}).get('preload', {}).get('check_in_date')

    def clean(self):
        super().clean()
        reservation_no = self.cleaned_data.get('reservation_no')
        check_in_date = self.cleaned_data.get('check_in_date')

        # validate required field
        if not reservation_no:
            self._errors['reservation_no'] = self.error_class([_('Enter the required information')])
        if not check_in_date:
            self._errors['check_in_date'] = self.error_class([_('Enter the required information')])
        # validate to backend
        if not self.errors:
            self.gateway_post()
        return self.cleaned_data

    def gateway_post(self):
        self.response = {
            'data': [{'pmsNo': '1234', 'otaNo': '1234', 'adults': 2, 'children': 0, 'roomType': 'Deluxe Room', 'roomNo': '0503', 'arrivalDate': '2022-06-02', 'departureDate': '2022-06-03', 'registrationDone': False, 'isFullHouse': False, 'hasCheckIn': False}]
        }
        return self.response
    
    def save(self):
        preload_data = dict(self.request.session.get('check_in', {}).get('preload', {})) # get and store preload because session will be cleared
        self.request.session['check_in'] = {} # clear session data
        self.request.session['check_in']['preload'] = preload_data # restore preload data
        self.request.session['check_in']['login'] = self.response.get('data', [])
        self.request.session['check_in']['input_reservation_no'] = self.cleaned_data.get('reservation_no')
        self.request.session['check_in']['input_check_in_date'] = self.cleaned_data.get('check_in_date').strftime('%Y-%m-%d')
        if 'preload' in self.request.session['check_in'] and 'auto_login' in self.request.session['check_in']['preload']:
            self.request.session['check_in']['auto_login'] = self.request.session['check_in']['preload']['auto_login'] # save auto login to session
            self.request.session['check_in']['preload']['auto_login'] = 0 # set auto login to False


class CheckInReservationForm(forms.Form):
    reservation_no = forms.ChoiceField(widget=forms.RadioSelect(), required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''
        self.reservation = {}
        self.response = {}
        self.fields['reservation_no'].choices = [(reservation.get('pmsNo', ''), reservation.get('pmsNo', '')) for reservation in self.request.session['check_in'].get('login', [])]

    def clean(self):
        super().clean()
        reservation_no = self.cleaned_data.get('reservation_no')
        if not reservation_no:
            self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class([_('No reservation selected.')])
        else:
            self.reservation = next((data for data in self.request.session['check_in'].get('login') if data.get('pmsNo', '') == reservation_no), {})
            if not self.reservation:
                self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class([_('No reservation selected.')])
            else:
                if not self.reservation.get('registrationDone', False): # no registration
                    self.reservation['status'] = 'registration'
                else:
                    # has registration and full house, or already checked-in, or checking in (check date is today from registration)
                    if self.reservation.get('isFullHouse', False) or self.reservation.get('hasCheckIn', False) or self.reservation.get('checking_in', False):
                        self.reservation['status'] = 'check_in'
                    elif not self.reservation.get('isFullHouse', False): # has registration but not full house
                        self.reservation['status'] = 'verification'
                self.gateway_post()
        return self.cleaned_data

    def gateway_post(self):
        self.response = {
                "data": {
                    "data": [
                        {
                            "pmsNo": "73978",
                            "reservationStatus": "DUEIN",
                            "adults": 2,
                            "children": 0,
                            "arrivalDate": "2022-06-09",
                            "departureDate": "2022-06-10",
                            "guestsList": [
                                {
                                    "guestId": 64901,
                                    "firstName": "Jacky",
                                    "lastName": "Chan",
                                    "isMainGuest": True,
                                    "dob": None,
                                    "nationality": None,
                                }
                            ],
                            "preArrivalDone": False,
                        }
                    ]
                }
            }
        return self.response

    def save(self):
        data = {}
        if self.reservation.get('status') == 'registration':
            data = next(iter(self.response.get('data', {}).get('data', [])))
        elif self.reservation.get('status') == 'check_in':
            data = next(iter(self.response.get('data', [])), {})
            data['status_code'] = self.response.get('statusCode', '')
        self.request.session['check_in']['reservation'] = {**self.reservation, **data}


class CheckInPreauthForm(forms.Form):
    card_no         = fields.CreditCardField(label=_('Card Number'))
    card_username   = forms.CharField(label=_('Name'))
    card_expiry     = forms.DateField(label=_('Expiration Date'), input_formats=['%m / %y', '%m / %Y'])
    card_code       = forms.CharField(label=_('CVC'))
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''

    def clean(self):
        super().clean()
        card_no = self.cleaned_data.get('card_no')
        card_username = self.cleaned_data.get('card_username')
        card_expiry = self.cleaned_data.get('card_expiry')
        card_code = self.cleaned_data.get('card_code')

        if not card_username:
            self._errors['card_username'] = self.error_class([_('Enter the required information')])
        if not card_expiry:
            self._errors['card_expiry'] = self.error_class([_('Enter the required information')])
        else:
            if card_expiry <= dt.date(dt.now()):
                self._errors['card_expiry'] = self.error_class([_('Your credit card is expired')])
        if not card_code:
            self._errors['card_code'] = self.error_class([_('Enter the required information')])
        return self.cleaned_data

    def save(self):
        self.request.session['check_in']['preauth'] = True # variable to prevent page jump


class CheckInPreauthCompleteForm(forms.Form):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''

    def save(self):
        self.request.session['check_in']['fr'] = False # variable to prevent page jump


class CheckInFrForm(forms.Form):
    fr_file = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''

    def save_file(self):
        file_name = self.request.session.session_key +'.png' # save fr file using `session_key` as file name
        folder_fr = os.path.join(settings.BASE_DIR, 'media', 'fr')
        if not os.path.exists(folder_fr):
            folder_media = os.path.join(settings.BASE_DIR, 'media')
            if not os.path.exists(folder_media):
                os.mkdir(folder_media)
            os.mkdir(folder_fr)
        saved_fr_file = os.path.join(folder_fr, file_name)
        file_data = base64.b64decode(self.cleaned_data.get('fr_file'))
        with open(saved_fr_file, 'wb') as f:
            f.write(file_data)
        self.file = saved_fr_file

    def clean(self):
        super().clean()
        fr_file = self.cleaned_data.get('fr_file')
        if not fr_file:
            self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class([_('No image file selected.')])
        else:
            self.save_file()
        return self.cleaned_data

    def gateway_fr(self):
        ocr_file_name = self.request.session.session_key +'.png'
        saved_ocr_file = os.path.join(settings.BASE_DIR, 'media', 'ocr', ocr_file_name)
        self.response = gateways.fr_endpoint(saved_ocr_file, self.file)
        return self.response

    def save(self):
        response = self.gateway_fr()
        self.request.session['check_in']['reservation']['fr_image'] = self.cleaned_data.get('fr_file')
        self.request.session['check_in']['reservation']['confidence'] = response.get('confidence')
        self.request.session['check_in']['reservation']['error_message'] = response.get('error_message')
        self.request.session['check_in']['fr'] = True # variable to prevent page jump

    

    

 