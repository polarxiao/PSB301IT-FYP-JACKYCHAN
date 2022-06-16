from django.urls    import path
from .views         import (RegistrationGuestListView, RegistrationDetailView, RegistrationOcrView,
                            RegistrationPreferenceView, RegistrationOtherInfoView)
                        


app_name = 'registration'
urlpatterns = [
    path('registration/guest_list/', RegistrationGuestListView.as_view(), name='guest_list'),
    path('registration/detail/<str:encrypted_id>/', RegistrationDetailView.as_view(), name='detail'),
    path('registration/ocr/<str:encrypted_id>/', RegistrationOcrView.as_view(), name='ocr'),
    path('registration/preference/', RegistrationPreferenceView.as_view(), name='preference'),
    path('registration/other_info/', RegistrationOtherInfoView.as_view(), name='other_info'),
]

