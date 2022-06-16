from django.urls    import path
from .views         import (IndexView, CheckInDataView, CheckInLoginView, CheckInReservationView,
                        CheckInPreAuthView, CheckInPreAuthCompleteView, CheckInFrView, CheckInCompleteView)

app_name = 'check_in'
urlpatterns = [
    path('check_in/', IndexView.as_view(), name='index'),
    path('check_in/data/', CheckInDataView.as_view(), name='data'),
    path('check_in/login/', CheckInLoginView.as_view(), name='login'),
    path('check_in/reservation/', CheckInReservationView.as_view(), name='reservation'),
    path('check_in/preauth/', CheckInPreAuthView.as_view(), name='preauth'),
    path('check_in/preauth_complete/', CheckInPreAuthCompleteView.as_view(), name='preauth_complete'),
    path('check_in/fr/', CheckInFrView.as_view(), name='fr'),
    path('check_in/complete/', CheckInCompleteView.as_view(), name='complete'),
]
