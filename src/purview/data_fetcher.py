from src.common.logger import get_logger

logger = get_logger(__name__)

class PurviewDataFetcher:
    def __init__(self, purview_client):
        self.purview_client = purview_client

    def scan_data_sources(self):
        try:
            response = self.purview_client.discovery.query("SELECT * FROM sys.databases")

            scan_results = []
            for data_source in response:
                data_source_name = data_source['name']
                scan_configuration = {
                    "properties": {
                        "scanRulesetName": "defaultScanRuleset",
                        "scanRulesetType": "System",
                        "scanTriggerType": "OnDemand"
                    }
                }
                scan_response = self.purview_client.discovery.scan.create_or_update_scan(data_source_name, scan_configuration)
                scan_results.append(scan_response)

            return scan_results
        except Exception as e:
            logger.error(f"Error initiating scan: {e}")
            raise

    def get_metadata(self):
        try:
            response = self.purview_client.discovery.query("SELECT * FROM sys.databases")
            return list(response)
        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            raise

    def get_data_insights(self):
        try:
            response = self.purview_client.discovery.query("SELECT * FROM sys.databases")
            return list(response)
        except Exception as e:
            logger.error(f"Error fetching data insights: {e}")
            raise