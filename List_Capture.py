import requests
import pandas as pd
import logging
from openpyxl.utils import get_column_letter

# Configure logging
logging.basicConfig(filename='metadata_fetch.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def load_credentials():
    """Load credentials from a file."""
    credentials = {}
    try:
        with open('credentials.txt', 'r') as file:
            for line in file:
                name, value = line.strip().split('=')
                credentials[name] = value
    except FileNotFoundError:
        logging.error("credentials.txt file not found.")
        raise
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        raise
    return credentials

def get_access_token(credentials):
    """Get access token from Azure AD using client credentials."""
    tenant_id = credentials['TENANT_ID']
    client_id = credentials['CLIENT_ID']
    client_secret = credentials['CLIENT_SECRET']
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
        logging.info("Access token retrieved successfully.")
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        logging.error(f"Response content: {response.content}")
        raise
    except Exception as e:
        logging.error(f"Error getting access token: {e}")
        raise

    return response.json()['access_token']

def get_data_from_endpoint(access_token, endpoint):
    """Fetch data from a given Microsoft Graph API endpoint."""
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(f'https://graph.microsoft.com/v1.0/{endpoint}', headers=headers)
        response.raise_for_status()
        logging.info(f"Data fetched from endpoint: {endpoint}")
        return response.json()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred while fetching data from {endpoint}: {err}")
        logging.error(f"Response content: {response.content}")
        raise
    except Exception as e:
        logging.error(f"Error fetching data from {endpoint}: {e}")
        raise

def add_y_columns(df):
    """Add a 'Y' column for each existing column."""
    for column in df.columns:
        df[f'{column}_Y'] = 'Y'
    return df

def save_to_excel(data_dict):
    """Save data to an Excel file."""
    file_path = 'all_metadata.xlsx'
    try:
        with pd.ExcelWriter(file_path) as writer:
            for sheet_name, data in data_dict.items():
                df = pd.DataFrame(data)
                df = add_y_columns(df)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                adjust_column_width(writer.book[sheet_name])
        logging.info(f"Data saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving data to Excel: {e}")
        raise

def adjust_column_width(sheet):
    """Adjust the column width of the Excel sheet to fit the content."""
    try:
        for column in sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column_letter].width = adjusted_width
        logging.info(f"Adjusted column widths for sheet: {sheet.title}")
    except Exception as e:
        logging.error(f"Error adjusting column widths: {e}")
        raise

def fetch_site_drive_items(access_token, site_id):
    """Fetch all items from the document library of a given SharePoint site."""
    drive_items = []
    endpoint = f'sites/{site_id}/drive/root/children'
    items = get_data_from_endpoint(access_token, endpoint).get('value', [])
    drive_items.extend(items)
    for item in items:
        if item.get('folder'):
            folder_id = item['id']
            folder_items = fetch_folder_items(access_token, site_id, folder_id)
            drive_items.extend(folder_items)
    return drive_items

def fetch_folder_items(access_token, site_id, folder_id):
    """Fetch all items from a given folder in a SharePoint document library."""
    endpoint = f'sites/{site_id}/drive/items/{folder_id}/children'
    return get_data_from_endpoint(access_token, endpoint).get('value', [])

def main():
    """Main function to fetch and store all metadata."""
    try:
        # Load credentials
        credentials = load_credentials()

        # Get access token
        access_token = get_access_token(credentials)
        print(f"Access Token: {access_token}")

        # Define endpoints to fetch data from
        endpoints = {
            'Users': 'users',
            'Groups': 'groups',
            'Teams': 'teams',
            'Sites': 'sites/root/sites',  # SharePoint sites
            'Channels': 'teams/{team_id}/channels',
            'Messages': 'teams/{team_id}/channels/{channel_id}/messages',
            'Files': 'sites/{site_id}/drive/items/{folder_id}/children'
        }

        data_dict = {}
        all_files = []
        all_channels = []
        all_messages = []

        # Fetch data from each endpoint
        for name, endpoint in endpoints.items():
            if name in ['Channels', 'Messages', 'Files']:
                continue

            data = get_data_from_endpoint(access_token, endpoint)
            if name == 'Sites':
                all_sites = data.get('value', [])
                data_dict[name] = all_sites

                # Fetch files from each site
                for site in all_sites:
                    site_id = site['id']
                    drive_items = fetch_site_drive_items(access_token, site_id)
                    all_files.extend(drive_items)
            elif name == 'Teams':
                all_teams = data.get('value', [])
                data_dict[name] = all_teams

                # Fetch channels and messages from each team
                for team in all_teams:
                    team_id = team['id']
                    channels = get_data_from_endpoint(access_token, f'teams/{team_id}/channels')
                    all_channels.extend(channels.get('value', []))
                    for channel in channels.get('value', []):
                        channel_id = channel['id']
                        messages = get_data_from_endpoint(access_token, f'teams/{team_id}/channels/{channel_id}/messages')
                        all_messages.extend(messages.get('value', []))
            else:
                data_dict[name] = data.get('value', []) if 'value' in data else [data]

        data_dict['Files'] = all_files
        data_dict['Channels'] = all_channels
        data_dict['Messages'] = all_messages

        # Save data to Excel
        save_to_excel(data_dict)

    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
        raise

if __name__ == "__main__":
    main()

