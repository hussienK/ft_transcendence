from django.conf import settings
from django.contrib.auth import login
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.providers.oauth2.client import OAuth2Error

from django.shortcuts import redirect
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from django.http import HttpResponse

class FortyTwoOAuthCallbackView(OAuth2CallbackView):
    def dispatch(self, request, *args, **kwargs):
        try:
            # Call the parent class's dispatch method
            return super().dispatch(request, *args, **kwargs)
        except OAuth2Error as e:
            return HttpResponse(f"OAuth2 authentication error: {str(e)}", status=400)

