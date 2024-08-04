import json
import pandas as pd
from src.teams_sharepoint.auth import AuthManager
from src.teams_sharepoint.data_fetcher import DataFetcher
from src.teams_sharepoint.data_processor import DataProcessor
from src.purview.client import PurviewClient
from src.purview.data_fetcher import PurviewDataFetcher
from src.purview.data_processor import PurviewDataProcessor
from src.scms.data_fetcher import SCMSDataFetcher
from src.sccm.data_fetcher import SCCMDataFetcher
from src.common.excel_handler import ExcelHandler
from src.common.logger import get_logger

logger = get_logger(__name__)

def load_credentials():
    """Load credentials from a JSON file."""
    try:
        with open('config/credentials.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("credentials.json file not found.")
        raise
    except json.JSONDecodeError:
        logger.error("Error parsing credentials.json file.")
        raise
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        raise

def process_teams_sharepoint_data(credentials):
    """Process Teams and SharePoint data."""
    try:
        auth_manager = AuthManager(credentials)
        access_token = auth_manager.get_access_token()
        data_fetcher = DataFetcher(access_token)

        endpoints = {
            'Users': 'users',
            'Groups': 'groups',
            'Teams': 'teams',
            'Sites': 'sites/root/sites',
        }

        data_dict = {}
        all_files = []
        all_channels = []
        all_messages = []

        for name, endpoint in endpoints.items():
            data = data_fetcher.get_data_from_endpoint(endpoint)
            if name == 'Sites':
                all_sites = data.get('value', [])
                data_dict[name] = all_sites

                for site in all_sites:
                    site_id = site['id']
                    drive_items = data_fetcher.fetch_site_drive_items(site_id)
                    all_files.extend(drive_items)
            elif name == 'Teams':
                all_teams = data.get('value', [])
                data_dict[name] = all_teams

                for team in all_teams:
                    team_id = team['id']
                    channels = data_fetcher.get_data_from_endpoint(f'teams/{team_id}/channels')
                    all_channels.extend(channels.get('value', []))
                    for channel in channels.get('value', []):
                        channel_id = channel['id']
                        messages = data_fetcher.get_data_from_endpoint(f'teams/{team_id}/channels/{channel_id}/messages')
                        all_messages.extend(messages.get('value', []))
            else:
                data_dict[name] = data.get('value', []) if 'value' in data else [data]

        data_dict['Files'] = all_files
        data_dict['Channels'] = all_channels
        data_dict['Messages'] = all_messages

        for key, value in data_dict.items():
            df = pd.DataFrame(value)
            df = DataProcessor.add_y_columns(df)
            data_dict[key] = df

        return data_dict
    except Exception as e:
        logger.error(f"Error processing Teams and SharePoint data: {e}")
        raise

def process_purview_data(credentials):
    """Process Purview data."""
    try:
        purview_client = PurviewClient(credentials).client
        data_fetcher = PurviewDataFetcher(purview_client)

        data_dict = {
            'Assets': data_fetcher.get_assets(),
            'Classifications': data_fetcher.get_classifications(),
            'Lineage': data_fetcher.get_lineage()
        }

        for key, value in data_dict.items():
            df = pd.DataFrame(value)
            df = PurviewDataProcessor.add_y_columns(df)
            data_dict[key] = df

        return data_dict
    except Exception as e:
        logger.error(f"Error processing Purview data: {e}")
        raise

def process_scms_data(credentials):
    """Process SCMS data."""
    try:
        scms_fetcher = SCMSDataFetcher(credentials)

        member_metadata = scms_fetcher.get_blockchain_member_metadata()
        nodes_metadata = scms_fetcher.get_blockchain_nodes_metadata()

        additional_filters = {
            'deployed_date': '2022-01-01'
        }
        contracts_metadata = scms_fetcher.get_blockchain_contracts_metadata(additional_filters)

        data_dict = {
            'Member Metadata': [member_metadata],
            'Nodes Metadata': nodes_metadata,
            'Contracts Metadata': contracts_metadata
        }

        for key, value in data_dict.items():
            df = pd.DataFrame(value)
            df.columns = [f"{col}_{key.lower().split()[0]}" for col in df.columns]
            df = DataProcessor.add_y_columns(df)
            data_dict[key] = df

        return data_dict
    except Exception as e:
        logger.error(f"Error processing SCMS data: {e}")
        raise

def process_sccm_data(credentials):
    """Process SCCM data."""
    try:
        sccm_fetcher = SCCMDataFetcher(credentials)

        hardware_inventory = sccm_fetcher.get_hardware_inventory()
        software_inventory = sccm_fetcher.get_software_inventory()
        backup_status = sccm_fetcher.get_backup_status()

        sccm_fetcher.close_connection()

        data_dict = {
            'Hardware Inventory': hardware_inventory,
            'Software Inventory': software_inventory,
            'Backup Status': backup_status
        }

        for key, df in data_dict.items():
            df = DataProcessor.add_y_columns(df)
            data_dict[key] = df

        return data_dict
    except Exception as e:
        logger.error(f"Error processing SCCM data: {e}")
        raise

def main():
    """Main function to orchestrate the data processing and saving."""
    try:
        logger.info("Starting metadata extraction process...")

        credentials = load_credentials()

        # Process Teams and SharePoint data
        logger.info("Processing Teams and SharePoint data...")
        teams_sharepoint_data = process_teams_sharepoint_data(credentials)
        ExcelHandler.save_to_excel(teams_sharepoint_data, 'all_metadata.xlsx')
        logger.info("Teams and SharePoint data saved to 'all_metadata.xlsx'")

        # Process Purview data
        logger.info("Processing Purview data...")
        purview_data = process_purview_data(credentials)
        ExcelHandler.save_to_excel(purview_data, 'purview_data.xlsx')
        logger.info("Purview data saved to 'purview_data.xlsx'")

        # Process SCMS data
        logger.info("Processing SCMS data...")
        scms_data = process_scms_data(credentials)
        ExcelHandler.save_to_excel(scms_data, 'blockchain_metadata.xlsx')
        logger.info("SCMS data saved to 'blockchain_metadata.xlsx'")

        # Process SCCM data
        logger.info("Processing SCCM data...")
        sccm_data = process_sccm_data(credentials)
        ExcelHandler.save_to_excel(sccm_data, 'sccm_data.xlsx')
        logger.info("SCCM data saved to 'sccm_data.xlsx'")

        # Filter Teams and SharePoint data
        logger.info("Filtering Teams and SharePoint data...")
        ExcelHandler.load_and_filter_excel('all_metadata.xlsx', 'filtered_metadata.xlsx')
        logger.info("Filtered Teams and SharePoint data saved to 'filtered_metadata.xlsx'")

        # Filter Purview data
        logger.info("Filtering Purview data...")
        ExcelHandler.load_and_filter_excel('purview_data.xlsx', 'filtered_purview_data.xlsx')
        logger.info("Filtered Purview data saved to 'filtered_purview_data.xlsx'")

        # Filter SCMS data
        logger.info("Filtering SCMS data...")
        ExcelHandler.load_and_filter_excel('blockchain_metadata.xlsx', 'filtered_blockchain_metadata.xlsx')
        logger.info("Filtered SCMS data saved to 'filtered_blockchain_metadata.xlsx'")

        # Filter SCCM data
        logger.info("Filtering SCCM data...")
        ExcelHandler.load_and_filter_excel('sccm_data.xlsx', 'filtered_sccm_data.xlsx')
        logger.info("Filtered SCCM data saved to 'filtered_sccm_data.xlsx'")

        logger.info("Metadata extraction process completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")
        raise

if __name__ == "__main__":
    main()