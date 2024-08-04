import requests
import logging
from src.common.logger import get_logger

logger = get_logger(__name__)

class AuthManager:
    def __init__(self, credentials):
        self.credentials = credentials

    def get_access_token(self):
        """Get access token from Azure AD using client credentials."""
        tenant_id = self.credentials['TENANT_ID']
        client_id = self.credentials['CLIENT_ID']
        client_secret = self.credentials['CLIENT_SECRET']
        token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        try:
            response = requests.post(token_url, headers=headers, data=body)
            response.raise_for_status()
            logger.info("Access token retrieved successfully.")
            return response.json()['access_token']
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error occurred: {err}")
            logger.error(f"Response content: {response.content}")
            raise
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise