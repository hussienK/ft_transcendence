from django.apps import AppConfig

class FortyTwoOAuthConfig(AppConfig):
    name = 'forty_two_oauth'

    def ready(self):
        from .providers.oauth2 import FortyTwoProvider
        from allauth.socialaccount.providers import registry
        registry.register(FortyTwoProvider)