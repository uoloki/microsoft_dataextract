import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.cosmos import CosmosClient
from src.common.logger import get_logger

logger = get_logger(__name__)

class SCMSDataFetcher:
    def __init__(self, credentials):
        self.credentials = credentials
        self.resource_client = ResourceManagementClient(
            DefaultAzureCredential(),
            credentials['AZURE_SUBSCRIPTION_ID']
        )

    def get_blockchain_member_metadata(self):
        try:
            member = self.resource_client.resources.get(
                resource_group_name=self.credentials['AZURE_RESOURCE_GROUP_NAME'],
                resource_provider_namespace='Microsoft.Blockchain',
                parent_resource_path='',
                resource_type='blockchainMembers',
                resource_name=self.credentials['AZURE_BLOCKCHAIN_MEMBER_NAME'],
                api_version='2018-06-01-preview'
            )
            return member.serialize(True)
        except Exception as e:
            logger.error(f"Error fetching blockchain member metadata: {e}")
            return {}

    def get_blockchain_nodes_metadata(self):
        try:
            nodes = self.resource_client.resources.list_by_resource_group(
                resource_group_name=self.credentials['AZURE_RESOURCE_GROUP_NAME'],
                filter=f"resourceType eq 'Microsoft.Blockchain/blockchainNodes' and substringof('{self.credentials['AZURE_BLOCKCHAIN_MEMBER_NAME']}', name)"
            )
            return [node.serialize(True) for node in nodes]
        except Exception as e:
            logger.error(f"Error fetching blockchain nodes metadata: {e}")
            return []

    def get_blockchain_contracts_metadata(self, additional_filters=None):
        try:
            client = CosmosClient(self.credentials['COSMOS_DB_ENDPOINT'], self.credentials['COSMOS_DB_KEY'])
            database = client.get_database_client(self.credentials['COSMOS_DB_DATABASE_NAME'])
            container = database.get_container_client(self.credentials['COSMOS_DB_CONTAINER_NAME'])

            query = "SELECT * FROM c WHERE c.blockchain_member = @blockchain_member"
            parameters = [{'name': '@blockchain_member', 'value': self.credentials['AZURE_BLOCKCHAIN_MEMBER_NAME']}]

            if additional_filters:
                for filter_name, filter_value in additional_filters.items():
                    query += f" AND c.{filter_name} = @{filter_name}"
                    parameters.append({'name': f'@{filter_name}', 'value': filter_value})

            contracts = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))

            return contracts
        except Exception as e:
            logger.error(f"Error fetching blockchain contracts metadata: {e}")
            return []