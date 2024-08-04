from azure.identity import ClientSecretCredential
from azure.purview.catalog import PurviewCatalogClient
from src.common.logger import get_logger

logger = get_logger(__name__)

class PurviewClient:
    def __init__(self, credentials):
        self.credentials = credentials
        self.client = self._connect_to_purview()

    def _connect_to_purview(self):
        try:
            credential = ClientSecretCredential(
                tenant_id=self.credentials['AZURE_TENANT_ID'],
                client_id=self.credentials['AZURE_CLIENT_ID'],
                client_secret=self.credentials['AZURE_CLIENT_SECRET']
            )

            purview_account_name = self.credentials['PURVIEW_ACCOUNT_NAME']
            purview_client = PurviewCatalogClient(
                endpoint=f"https://{purview_account_name}.purview.azure.com",
                credential=credential
            )

            return purview_client
        except Exception as e:
            logger.error(f"Error connecting to Microsoft Purview: {e}")
            raise