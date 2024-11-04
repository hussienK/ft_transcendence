from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .oauth2 import FortyTwoProvider

urlpatterns = default_urlpatterns(FortyTwoProvider)