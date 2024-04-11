import boto3
from airflow.hooks.base_hook import BaseHook
import hvac

class VaultHook(BaseHook):
    def __init__(self, aws_secret_id, vault_conn_id='vault_default'):
        super().__init__(source=None)
        self.vault_conn_id = vault_conn_id
        self.aws_secret_id = aws_secret_id
        self.client = None

    def get_conn(self):
        """Establishes a connection to Vault using a token retrieved from AWS Secrets Manager."""
        if not self.client:
            # Fetch the connection object from Airflow's backend
            conn = self.get_connection(self.vault_conn_id)
            url = conn.host

            # Retrieve the Vault token from AWS Secrets Manager
            session = boto3.session.Session()
            client = session.client(service_name='secretsmanager')
            get_secret_value_response = client.get_secret_value(SecretId=self.aws_secret_id)
            token = get_secret_value_response['SecretString']

            self.client = hvac.Client(url=url, token=token)
            if not self.client.is_authenticated():
                raise Exception("Failed to authenticate with Vault")

        return self.client
