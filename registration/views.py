from django.conf                    import settings
from django.http                    import Http404
from django.shortcuts               import redirect
from django.urls                    import reverse, reverse_lazy
from django.utils.translation       import gettext_lazy as _
from django.views.generic           import *
from core                           import utils
from core.mixins                    import PropertyRequiredMixin, RequestFormKwargsMixin, JSONResponseMixin
from check_in.mixins                import ParameterRequiredMixin
from .forms                         import (RegistrationGuestListForm, RegistrationDetailForm, RegistrationOcrForm,
                                            RegistrationPreferenceForm, RegistrationOtherInfoForm)


class RegistrationGuestListView(ParameterRequiredMixin, PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'registration/guest_list.html'
    form_class              = RegistrationGuestListForm
    success_url             = reverse_lazy('registration:preference')
    parameter_required      = 'check_in.reservation'

    def get(self, request, *args, **kwargs):
        self.request.session['registration'] = {} # initiate and remove unsaved `detail` if any
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        max_guest = int(self.request.session['check_in']['reservation'].get('adults', 1)) + int(self.request.session['check_in']['reservation'].get('children', 0))
        context['add_guest'] = max_guest > len(self.request.session['check_in']['reservation'].get('guestsList', []))
        context['can_submit'] = all([guest.get('is_done', False) or guest.get('hasLocalRecord', False) for guest in self.request.session['check_in']['reservation'].get('guestsList', [])])
        return context

    def form_valid(self, form):
        form.save()
        if form.errors:
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.session['check_in']['reservation'].get('preArrivalDone'):
            self.success_url = reverse('registration:complete') # skip `other info` and redirect to `complete` page
        return super().get_success_url()


class RegistrationDetailView(PropertyRequiredMixin, RequestFormKwargsMixin, UpdateView):
    template_name           = 'registration/detail.html'
    form_class              = RegistrationDetailForm
    success_url             = reverse_lazy('registration:guest_list')

    def get_object(self):
        guest_id = utils.decrypt(self.kwargs.get('encrypted_id', '')) # `0` for new guest
        guest = self.request.session['registration'].get('detail', {})
        if str(guest.get('id', '')) != guest_id: # not from `passport` page
            if guest_id != '0': # existing guest
                guest = next((dict(data) for data in self.request.session['check_in']['reservation'].get('guestsList', {}) if str(data.get('guestId', '')) == guest_id or data.get('new_guest_id') == guest_id), {})
            else: # new guest
                guest = {}
                guest['guestId'] = 0
        if not guest:
            raise Http404('Not found')
        guest['id'] = guest.get('guestId', 0) # assign `id` from `guestId` as identifier
        self.request.session['registration']['detail'] = guest # assigned as separate object for not overwriting `reservation` session
        return self.request.session['registration']['detail']

    def dispatch(self, request, *args, **kwargs):
        guest_id = utils.decrypt(self.kwargs.get('encrypted_id', '')) # `0` for new guest
        if guest_id == '0': # adding new guest
            max_guest = int(self.request.session['check_in']['reservation'].get('adults', 1)) + int(self.request.session['check_in']['reservation'].get('children', 0))
            if max_guest <= len(self.request.session['check_in']['reservation'].get('guestsList', [])):
                return redirect('registration:guest_list') # redirect to guest list if max guests is exceeded
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ocr_required'] = True
        context['bootstrap_datepicker_language'] = 'en-us'
        guest_id = utils.decrypt(self.kwargs.get('encrypted_id', '')) # 0 for new guest
        context['ga_ocr_success'] = self.object.get('idImage') and str(self.object.get('id', '')) == guest_id # from `passport` page
        context['custom_request_path'] = '/registration/detail/'
        return context

    def get_success_url(self):
        if not self.success_url:
            return super().get_success_url()
        url = self.success_url.format(**self.object)
        if not self.request.POST.get('is_submit', False):
            url = reverse('registration:ocr', kwargs={'encrypted_id': self.kwargs.get('encrypted_id', '')})
        return url


class RegistrationOcrView(PropertyRequiredMixin, RequestFormKwargsMixin, UpdateView):
    template_name           = 'registration/ocr.html'
    form_class              = RegistrationOcrForm

    def get_object(self):
        guest_id = utils.decrypt(self.kwargs.get('encrypted_id', '')) # 0 for creation
        guest = self.request.session['registration']['detail']
        if str(guest.get('id', '')) != guest_id and guest.get('new_guest_id') != guest_id:
            raise Http404('Not found')
        return guest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['encrypted_id'] = self.kwargs.get('encrypted_id', '')
        context['custom_request_path'] = '/registration/ocr/'
        return context

    def get_success_url(self):
        url = reverse('registration:detail', kwargs={'encrypted_id': self.kwargs.get('encrypted_id', '')})
        return url


class RegistrationPreferenceView(ParameterRequiredMixin, PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'registration/preference.html'
    form_class              = RegistrationPreferenceForm
    success_url             = reverse_lazy('registration:other_info')
    parameter_required      = 'registration.guest_list'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class RegistrationOtherInfoView(ParameterRequiredMixin, PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'registration/other_info.html'
    form_class              = RegistrationOtherInfoForm
    success_url             = reverse_lazy('check_in:preauth')
    parameter_required      = 'registration.preference'
    
    def form_valid(self, form):
        form.save()
        if form.errors:
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tnc_link'] = settings.TNC_LINK
        context['privacy_link'] = settings.PRIVACY_LINK
        return context

