from django.shortcuts   import redirect


class ParameterRequiredMixin:
    """
    View mixin that verifies the user has `parameter_required` in session.
    `parameter_required` is divided into `module` and `page` with `.` 
    separator. Validator will check if both `module` and `page` is not `None` 
    otherwise will be redirected `login` page. And will be redirected to 
    particular page if `page` does not exist in session.
    """
    parameter_required = None

    def dispatch(self, request, *args, **kwargs):
        parameter_required_iter = iter(self.parameter_required.split('.'))
        module, page = next(parameter_required_iter, None), next(parameter_required_iter, None)
        if not module or not page:
            return redirect('check_in:login')
        if not request.session.get(module, {}).get(page, ''):
            return redirect('%s:%s' % (module, page))
        return super().dispatch(request, args, kwargs)
