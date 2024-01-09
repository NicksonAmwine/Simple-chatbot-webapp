import os
from dotenv import load_dotenv


load_dotenv('secrets.env')

print('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:', os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'))
print('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET:', os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'))
print('openai_key:', os.environ.get('OPENAI_API_KEY'))
print('SECRET_KEY:', os.environ.get('SECRET_KEY'))