from django.urls    import path
from .views         import IndexView, CorePropertyView

app_name = 'core'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('property/', CorePropertyView.as_view(), name='property'),
]