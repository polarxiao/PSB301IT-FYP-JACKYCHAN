from django.conf                import settings
from django.urls                import reverse
from django.utils.translation   import gettext_lazy as _
from django.views.generic       import *
from .forms                     import CorePropertyForm
from .mixins                    import RequestFormKwargsMixin


class IndexView(RedirectView):
    pattern_name = 'core:property'

class CorePropertyView(RequestFormKwargsMixin, FormView):
    template_name   = 'core/property.html'
    form_class      = CorePropertyForm

    def dispatch(self, request, *args, **kwargs):
        properties = settings.HOTEL_PROPERTIES
        if len(properties) == 1: # auto submit
            prop = next(iter(properties), None)
            data = {}
            data['property_id'] = prop.get('id', None)
            form = self.get_form_class()
            form = form(request, data)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = settings.HOTEL_PROPERTIES
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        self.success_url = reverse('check_in:data')
        next_url = self.request.GET.get('next', None)
        if next_url:
            self.success_url = next_url
        return super().get_success_url()

