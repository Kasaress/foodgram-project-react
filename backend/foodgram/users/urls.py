from django.urls import include, path
from .views import (RegisterView)

app_name = 'users'

# urlpatterns_auth = [
#     path('token/login', RegisterView.as_view()),
#     # path('token/loguot', )
# ]

urlpatterns = [
    # path('auth/', include(urlpatterns_auth)),
    # path('v1/', include(router_v1.urls)),
    path('', RegisterView.as_view()),
]