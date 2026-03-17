"""
WSGI config for outfit_recommendation project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'outfit_recommendation.settings')
application = get_wsgi_application()
