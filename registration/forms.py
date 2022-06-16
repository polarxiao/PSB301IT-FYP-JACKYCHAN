import base64
import os
from django                     import forms
from django.conf                import settings
from django.utils.translation   import gettext_lazy as _
from django_countries.fields    import Country, CountryField
from core                       import gateways, utils


class RegistrationGuestListForm(forms.Form):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''
        self.remaining_reservations = []

    def clean(self):
        super().clean()
        return self.cleaned_data

    def save(self):
        self.request.session['registration']['guest_list'] = True


class RegistrationDetailForm(forms.Form):
    first_name = forms.CharField(label=_('First Name'), required=False)
    last_name = forms.CharField(label=_('Last Name'), required=False)
    id_no = forms.CharField(label=_('Passport Number'), required=False)
    nationality = CountryField(blank_label='-').formfield(label=_('Nationality'), required=False)
    birth_date = forms.DateField(label=_('Date of Birth'), required=False)
    is_overwrite = forms.BooleanField(initial=True, required=False)
    is_submit = forms.BooleanField(initial=True, required=False)

    def __init__(self, instance, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.request = request
        self.label_suffix = ''
        # from instance
        first_name = self.instance.get('firstName', '')
        last_name = self.instance.get('lastName', '')
        id_no = self.instance.get('idNo', '')
        nationality = self.instance.get('nationality', '')
        birth_date = self.instance.get('dob', '')
        # from `preload`
        if self.instance.get('isMainGuest', False):
            first_name = self.request.session.get('registration', {}).get('preload', {}).get('first_name', first_name)
            id_no = self.request.session.get('registration', {}).get('preload', {}).get('id_no', id_no)
            nationality = self.request.session.get('registration', {}).get('preload', {}).get('nationality', nationality)
            birth_date = self.request.session.get('registration', {}).get('preload', {}).get('birth_date', birth_date)
        # from `ocr`
        if self.instance.get('is_overwrite', False):
            first_name = self.request.session.get('registration', {}).get('ocr', {}).get('first_name', first_name)
            if self.instance.get('guestId', 0) == 0:
                last_name = self.request.session.get('registration', {}).get('ocr', {}).get('last_name', last_name)
            id_no = self.request.session.get('registration', {}).get('ocr', {}).get('number', id_no)
            nationality = Country(self.request.session.get('registration', {}).get('ocr', {}).get('nationality', '')).code or nationality
            birth_date = self.request.session.get('registration', {}).get('ocr', {}).get('date_of_birth', birth_date)
        # assign
        self.fields['first_name'].initial = first_name.title()
        self.fields['last_name'].initial = last_name
        self.fields['id_no'].initial = id_no
        self.fields['nationality'].initial = nationality
        self.fields['birth_date'].initial = birth_date
    
    def clean(self):
        super().clean()
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        nationality = self.cleaned_data.get('nationality')
        id_no = self.cleaned_data.get('id_no')
        birth_date = self.cleaned_data.get('birth_date')
        is_submit = self.cleaned_data.get('is_submit')
        
        if is_submit:
            if not first_name:
                self._errors['first_name'] = self.error_class([_('Enter the required information')])
            if not last_name:
                self._errors['last_name'] = self.error_class([_('Enter the required information')])
            if not nationality:
                self._errors['nationality'] = self.error_class([_('Enter the required information')])
            if not id_no:
                self._errors['id_no'] = self.error_class([_('Enter the required information')])
            if not birth_date:
                self._errors['birth_date'] = self.error_class([_('Enter the required information')])
        return self.cleaned_data

    def save(self):
        self.instance['firstName'] = self.cleaned_data.get('first_name')
        self.instance['lastName'] = self.cleaned_data.get('last_name')
        self.instance['nationality'] = self.cleaned_data.get('nationality')
        self.instance['idNo'] = self.cleaned_data.get('id_no')
        self.instance['dob'] = self.cleaned_data.get('birth_date').strftime('%Y-%m-%d') if self.cleaned_data.get('birth_date') else ''
        self.instance['is_overwrite'] = self.cleaned_data.get('is_overwrite')
        if self.cleaned_data.get('is_submit', False):
            if self.instance.get('guestId', 0) != 0 or self.instance.get('new_guest_id', None): # existing guest
                if self.instance.get('id', 0) != 0: # existing guest from pms
                    guest = next((data for data in self.request.session['check_in']['reservation'].get('guestsList', []) if data.get('guestId', None) == self.instance.get('id', 0)), {})
                else: # existing guest from newly added data
                    guest = next((data for data in self.request.session['check_in']['reservation'].get('guestsList', []) if data.get('new_guest_id', '') == self.instance.get('new_guest_id', None)), {})
                guest['firstName'] = self.instance.get('firstName', '')
                guest['lastName'] = self.instance.get('lastName', '')
                guest['nationality'] = self.instance.get('nationality', '')
                guest['nationalityThreeLetters'] = Country(self.instance.get('nationality')).alpha3
                guest['idNo'] = self.instance.get('idNo', '')
                guest['dob'] = self.instance.get('dob', '')
                guest['idImage'] = self.instance.get('idImage', '')
                guest['idType'] = self.instance.get('idType', '')
                guest['is_done'] = True
            else: # new guest
                guest = {}
                guest['guestId'] = self.instance.get('guestId', 0)
                guest['firstName'] = self.instance.get('firstName', '')
                guest['lastName'] = self.instance.get('lastName', '')
                guest['nationality'] = self.instance.get('nationality', '')
                guest['nationalityThreeLetters'] = Country(self.instance.get('nationality')).alpha3
                guest['idNo'] = self.instance.get('idNo', '')
                guest['dob'] = self.instance.get('dob', '')
                guest['idImage'] = self.instance.get('idImage', '')
                guest['idType'] = self.instance.get('idType', '')
                guest['new_guest_id'] = 'new%s' % len([data for data in self.request.session['check_in']['reservation'].get('guestsList', []) if data.get('guestId', 0) == 0])
                guest['is_done'] = True
                self.request.session['check_in']['reservation']['guestsList'].append(guest)
        return self.instance


class RegistrationOcrForm(forms.Form):
    ocr_file = forms.CharField(widget=forms.HiddenInput(), required=False)

    error_messages = {
        'Wrong API Key': _('Incorrect API key'),
        'Error scanning image. Please try again later.': _('Error scanning image. Please try again later.'),
        'Image size is too big.': _('Image file is too big.'),
        'Invalid passport image. MRZ Code is invalid.': _('Invalid passport image. MRZ Code is invalid.'),
        'Invalid NRIC image.': _('Invalid NRIC image.'),
        'Face image not found.': _('Invalid passport image. Please make sure your passport page area is not blocked.'),
    }

    def __init__(self, instance, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.request = request
        self.label_suffix = ''
        self.response = {}
        self.file = None
        self.request.session['registration']['ocr'] = {} # initiate `ocr`

    def clean(self):
        super().clean()
        ocr_file = self.cleaned_data.get('ocr_file')

        if not ocr_file:
            self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class([_('No image file selected.')])
        else:
            # validate based on `scan_type` (`passport` / `nric`)
            self.save_file()
            self.gateway_ocr()
            if self.response.get('success'):
                result = self.response.get('result', {})
                if result.get('document_type', 'passport') == 'passport' and result.get('expired', True):
                    self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class([_('Your passport has expired, please capture / upload a valid passport photo to proceed')])
            else:
                response_message = self.response.get('errorMessage', _('Unknown error'))
                self._errors[forms.forms.NON_FIELD_ERRORS] = self.error_class([self.error_messages.get(response_message, response_message)])
            
            if self._errors: # remove saved file if fail
                os.remove(self.file)

        return self.cleaned_data

    def save_file(self):
        file_name = self.request.session.session_key +'.png' # save ocr file using `session_key` as file name
        folder_ocr = os.path.join(settings.BASE_DIR, 'media', 'ocr')
        if not os.path.exists(folder_ocr):
            folder_media = os.path.join(settings.BASE_DIR, 'media')
            if not os.path.exists(folder_media):
                os.mkdir(folder_media)
            os.mkdir(folder_ocr)
        saved_file = os.path.join(folder_ocr, file_name)
        file_data = base64.b64decode(self.cleaned_data.get('ocr_file'))
        with open(saved_file, 'wb') as f:
            f.write(file_data)
        self.file = saved_file

    def gateway_ocr(self):
        self.response = gateways.ocr(self.file)

    def save(self):
        with open(self.file, 'rb') as image_file:
            file_b64_encoded = base64.b64encode(image_file.read())
        self.instance['idImage'] = file_b64_encoded.decode()
        self.instance['idType'] = 'PASSPORT' if self.response.get('result', {}).get('document_type') == 'passport' else 'IC'
        self.request.session['check_in']['reservation']['idImage'] = self.instance['idImage']
        self.request.session['registration']['ocr'] = self.response.get('result', {})
        return self.instance


class RegistrationPreferenceForm(forms.Form):
    arrival_time        = forms.ChoiceField(label=_('Time of Arrival'), required=False)
    special_requests    = forms.CharField(label=_('Special Requests'), required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''
        self.fields['arrival_time'].choices = utils.generate_arrival_time()
        self.fields['arrival_time'].initial = utils.parse_arrival_time(self.request.session['check_in']['reservation'].get('eta', ''))
        self.fields['special_requests'].initial = self.request.session['check_in']['reservation'].get('comments', '')
        data = {}
        data['roomType'] = self.request.session['check_in']['reservation'].get('roomType')

    def clean(self):
        super().clean()
        arrival_time = self.cleaned_data.get('arrival_time')

        if not arrival_time:
            self._errors['arrival_time'] = self.error_class([_('Enter the required information')])
        return self.cleaned_data

    def save(self):
        arrival_time = self.cleaned_data.get('arrival_time')
        special_requests = self.cleaned_data.get('special_requests')

        self.request.session['check_in']['reservation']['eta'] = arrival_time + ':00'
        self.request.session['check_in']['reservation']['comments'] = special_requests
        self.request.session['registration']['preference'] = True # variable to prevent page jump


class RegistrationOtherInfoForm(forms.Form):
    email               = forms.EmailField(label=_('Email'), required=False)
    is_agreed_tnc       = forms.BooleanField(label=_('Is Agreed'), required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.label_suffix = ''
        self.remaining_reservations = []
        main_guest = next((guest for guest in self.request.session['check_in']['reservation'].get('guestsList', []) if guest.get('isMainGuest', False)), {})

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')
        is_agreed_tnc = self.cleaned_data.get('is_agreed_tnc', False)

        if not email:
            self._errors['email'] = self.error_class([_('Enter the required information')])
        if not is_agreed_tnc:
            self._errors['is_agreed_tnc'] = self.error_class([_('Please acknowledge Terms & Conditions requirement')])

        return self.cleaned_data

    def save(self):
        email = self.cleaned_data.get('email')

        main_guest = next((guest for guest in self.request.session['check_in']['reservation'].get('guestsList', []) if guest.get('isMainGuest', False)), {})
        main_guest.update({'email': email})
        self.request.session['registration']['other_info'] = True # variable to prevent page jump