"""Cust OAuth adpater."""

import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultSocialAccountAdapter):
    """Custom Sociaal account adapter."""
