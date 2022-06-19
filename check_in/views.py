from django.conf                import settings
from django.shortcuts           import render, redirect
from django.urls                import reverse, reverse_lazy
from django.utils.translation   import gettext, gettext_lazy as _
from django.views.generic       import *
from core                       import utils
from core.views                 import IndexView
from core.mixins                import PropertyRequiredMixin, RequestFormKwargsMixin
from .forms                     import (CheckInLoginForm, CheckInReservationForm,
                                        CheckInPreauthForm, CheckInPreauthCompleteForm, CheckInFrForm)
from .mixins                    import ParameterRequiredMixin


class IndexView(IndexView):
    pattern_name = 'check_in:login'


class CheckInDataView(RedirectView):
    pattern_name = 'check_in:login'

    def get(self, request, *args, **kwargs):
        request.session['check_in'] = {'preload': {}}
        if 'property' in request.GET: request.session['property_id'] = request.GET.get('property', None)
        if 'reservation_no' in request.GET: request.session['check_in']['preload']['reservation_no'] = request.GET.get('reservation_no', '')
        if 'check_in_date' in request.GET: request.session['check_in']['preload']['check_in_date'] = request.GET.get('check_in_date', '')
        if 'selected_reservation_no' in request.GET: request.session['check_in']['preload']['selected_reservation_no'] = request.GET.get('selected_reservation_no', '')
        return super().get(request, *args, **kwargs)


class CheckInLoginView(PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'check_in/login.html'
    form_class              = CheckInLoginForm
    success_url             = reverse_lazy('check_in:reservation')
    progress_bar_module     = 'check_in'

    def dispatch(self, request, *args, **kwargs):
        if request.session.get('check_in', {}).get('preload', {}).get('auto_login', 0):
            data = {}
            data['reservation_no'] = request.session.get('check_in', {}).get('preload', {}).get('reservation_no', '')
            data['check_in_date'] = request.session.get('check_in', {}).get('preload', {}).get('check_in_date', '')
            form = self.get_form_class()
            form = form(request, data)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CheckInReservationView(ParameterRequiredMixin, PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'check_in/reservation.html'
    form_class              = CheckInReservationForm
    success_url             = reverse_lazy('check_in:preauth')
    parameter_required      = 'check_in.login'

    def dispatch(self, request, *args, **kwargs):
        data = {}
        if len(request.session.get('check_in', {}).get('login', [])) == 1:
            data['reservation_no'] = next(iter(request.session.get('check_in', {}).get('login', [])), {}).get('pmsNo', '')
        if request.session.get('check_in', {}).get('preload', {}).get('selected_reservation_no', None):
            # using `pop` to prevent issue when clicking on back button
            data['reservation_no'] = request.session.get('check_in', {}).get('preload', {}).pop('selected_reservation_no', None)
        form = self.get_form_class()
        form = form(request, data)
        if form.is_valid():
            return self.form_valid(form)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservations'] = []
        for reservation in self.request.session['check_in'].get('login', []):
            reservation = dict(reservation) # create new variable to prevent modification on `request.session`
            reservation['formattedArrivalDate'] = utils.format_display_date(reservation.get('arrivalDate', ''))
            reservation['formattedDepartureDate'] = utils.format_display_date(reservation.get('departureDate', ''))
            context['reservations'].append(reservation)
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.session['check_in']['reservation'].get('status') == 'registration':
            self.success_url = reverse('registration:guest_list')
        return super().get_success_url()


class CheckInPreAuthView(ParameterRequiredMixin, PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'check_in/preauth.html'
    form_class              = CheckInPreauthForm
    success_url             = reverse_lazy('check_in:preauth_complete')
    parameter_required      = 'registration.other_info'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

class CheckInPreAuthCompleteView(ParameterRequiredMixin, PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'check_in/preauth_complete.html'
    form_class              = CheckInPreauthCompleteForm
    success_url             = reverse_lazy('check_in:fr')
    parameter_required      = 'check_in.preauth'

    def form_valid(self, form):
        form.save()
        if form.errors:
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def get_success_url(self):
        if self.request.session['check_in'].get('fr'):
            self.success_url = reverse('check_in:complete')
        return super().get_success_url()


class CheckInFrView(ParameterRequiredMixin, PropertyRequiredMixin, RequestFormKwargsMixin, FormView):
    template_name           = 'check_in/fr.html'
    form_class              = CheckInFrForm
    success_url             = reverse_lazy('check_in:complete')
    parameter_required      = 'check_in.preauth'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tnc_link'] = settings.TNC_LINK
        context['privacy_link'] = settings.PRIVACY_LINK
        return context

    def form_valid(self, form):
        form.save()
        if form.errors:
            return self.form_invalid(form)
        return super().form_valid(form)


class CheckInCompleteView(TemplateView):
    template_name = 'check_in/complete.html'

