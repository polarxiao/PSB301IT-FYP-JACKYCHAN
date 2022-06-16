from django.template            import Library
from core          import utils

register = Library()

@register.filter()
def encrypt(value):
    return utils.encrypt(value)
