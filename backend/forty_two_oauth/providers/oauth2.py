from allauth.socialaccount.providers.oauth.provider import OAuthProvider

class FortyTwoProvider(OAuthProvider):
    id = '42'
    name = '42'

    def extract_uid(self, data):
        return str(data['id'])
    
    def edxtract_common_fields(seld, data):
        #map 42 API fields to user fields
        return {
            'username': data.get('login'),
            'email': data.get('email'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
        }
    
    def get_default_scope(self):
        return ['public']