# Metadata Extractor

![Project Status](https://img.shields.io/badge/status-mock--up%20/%20in%20development-orange)

## Important Note

This project is currently a mock-up and the functionality is still being developed and tested. It is not yet ready for production use. The code and documentation are provided as a conceptual framework and are subject to significant changes as development progresses.

## Overview

Metadata Extractor is a comprehensive Python-based tool designed to extract, process, and analyze metadata from various Microsoft services and systems. It provides a unified interface to collect data from Teams, SharePoint, Microsoft Purview, Supply Chain Management System (SCMS), and System Center Configuration Manager (SCCM).

## Features

- Extract metadata from:
  - Microsoft Teams and SharePoint
  - Microsoft Purview
  - Supply Chain Management System (SCMS)
  - System Center Configuration Manager (SCCM)
- Logging system for tracking operations and errors

## Prerequisites

- Python 3.8 or higher
- Access to the Microsoft services mentioned above
- Necessary credentials and permissions for each service

## Installation

1. Clone the repository:
   `git clone https://github.com/uoloki/microsoft_dataextract.git`
   `cd metadata-extractor`

2. Install the required dependencies:
   `pip install -r requirements.txt`

3. Set up your credentials:
   - Create a credentials.json file in the config/ directory
   - Add your credentials for each service (see Configuration section below)

## Configuration

Create a credentials.json file in the config/ directory with the following structure:

```{
  "AZURE_TENANT_ID": "your_tenant_id",
  "AZURE_CLIENT_ID": "your_client_id",
  "AZURE_CLIENT_SECRET": "your_client_secret",
  "PURVIEW_ACCOUNT_NAME": "your_purview_account_name",
  "AZURE_SUBSCRIPTION_ID": "your_subscription_id",
  "AZURE_RESOURCE_GROUP_NAME": "your_resource_group_name",
  "AZURE_BLOCKCHAIN_MEMBER_NAME": "your_blockchain_member_name",
  "COSMOS_DB_ENDPOINT": "your_cosmos_db_endpoint",
  "COSMOS_DB_KEY": "your_cosmos_db_key",
  "COSMOS_DB_DATABASE_NAME": "your_database_name",
  "COSMOS_DB_CONTAINER_NAME": "your_container_name",
  "SCCM_SERVER": "your_sccm_server",
  "SCCM_DATABASE": "your_sccm_database",
  "SCCM_USERNAME": "your_sccm_username",
  "SCCM_PASSWORD": "your_sccm_password"
}```

Ensure that you have the necessary permissions and credentials for each service you plan to use.

## Usage

Run the main script:

`python main.py`

This will:
1. Extract metadata from all configured sources
2. Process and filter the data
3. Save both raw and filtered data to Excel files

## Output

The script generates several Excel files:
- all_metadata.xlsx: Raw data from Teams and SharePoint
- purview_data.xlsx: Raw data from Microsoft Purview
- blockchain_metadata.xlsx: Raw data from SCMS
- sccm_data.xlsx: Raw data from SCCM

## Project Structure

`metadata_extractor/
│
├── src/
│   ├── teams_sharepoint/
│   ├── purview/
│   ├── scms/
│   ├── sccm/
│   └── common/
│
├── tests/
├── config/
├── main.py
├── requirements.txt
└── README.md`

## To-Do

The following items are planned for future development:

1. Add comprehensive unit tests for all modules to ensure code reliability and ease of maintenance.
   - Some modules are outdated and should be changed
   - Filtering functionality is excessive, as it is being invoked after extraction

2. Improve code reusability:
   - Implement a base class for data fetchers to reduce code duplication
   - Create a common authentication module for different services
   - Develop shared utility functions for common operations

3. Implement a function for selecting desired datapoints:
   - Replace hardcoded datapoint selection with a configurable approach
   - Allow users to specify which datapoints to extract via a configuration file or command-line arguments


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.