from django.conf        import settings
from django.http        import JsonResponse
from django.shortcuts   import redirect
from django.urls        import reverse


class PropertyRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if 'property_id' in request.session and request.session['property_id']:
            prop = next((prop_data for prop_data in settings.HOTEL_PROPERTIES or [] if prop_data.get('id') == request.session['property_id']), {})
            if prop:
                return super().dispatch(request, *args, **kwargs)
        return redirect(reverse('core:property') + '?next=' + request.path)


class RequestFormKwargsMixin:

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(request=self.request)
        return kwargs


class JSONResponseMixin:

    json_status = None
    json_errors = []
    json_data   = {}

    def render_to_json_response(self, context, **response_kwargs):
        """ Returns a JSON response, transforming 'context' to make the payload. """
        return JsonResponse(self.get_json_data(context), **response_kwargs)

    def get_json_data(self, context):
        """ Returns an object that will be serialized as JSON by json.dumps(). """
        data = self.json_data
        data['status'] = self.json_status or 'error'
        data['errors'] = self.json_errors
        return data
