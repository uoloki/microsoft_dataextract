import requests
from src.common.logger import get_logger

logger = get_logger(__name__)

class DataFetcher:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://graph.microsoft.com/v1.0/'

    def get_data_from_endpoint(self, endpoint):
        """Fetch data from a given Microsoft Graph API endpoint."""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        try:
            response = requests.get(f'{self.base_url}{endpoint}', headers=headers)
            response.raise_for_status()
            logger.info(f"Data fetched from endpoint: {endpoint}")
            return response.json()
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error occurred while fetching data from {endpoint}: {err}")
            logger.error(f"Response content: {response.content}")
            raise
        except Exception as e:
            logger.error(f"Error fetching data from {endpoint}: {e}")
            raise

    def fetch_site_drive_items(self, site_id):
        """Fetch all items from the document library of a given SharePoint site."""
        drive_items = []
        endpoint = f'sites/{site_id}/drive/root/children'
        items = self.get_data_from_endpoint(endpoint).get('value', [])
        drive_items.extend(items)
        for item in items:
            if item.get('folder'):
                folder_id = item['id']
                folder_items = self.fetch_folder_items(site_id, folder_id)
                drive_items.extend(folder_items)
        return drive_items

    def fetch_folder_items(self, site_id, folder_id):
        """Fetch all items from a given folder in a SharePoint document library."""
        endpoint = f'sites/{site_id}/drive/items/{folder_id}/children'
        return self.get_data_from_endpoint(endpoint).get('value', [])