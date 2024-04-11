# Filename: hooks/vault_hook.py
from airflow.hooks.base_hook import BaseHook
import hvac
import boto3
import json

class VaultHook(BaseHook):
    def __init__(self, aws_secret_name, vault_secrets_file):
        super().__init__()
        self.aws_secret_name = aws_secret_name
        self.vault_secrets_file = vault_secrets_file
        self.client = None

    def get_vault_config(self):
        """Retrieve Vault configuration from AWS Secrets Manager."""
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager')
        response = client.get_secret_value(SecretId=self.aws_secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        else:
            raise Exception("Vault configuration not found in AWS Secrets Manager.")

    def get_conn(self):
        """Establishes a connection to Vault."""
        if not self.client:
            vault_config = self.get_vault_config()
            self.client = hvac.Client(url=vault_config['vault_url'], token=vault_config['vault_token'])
            if not self.client.is_authenticated():
                raise Exception("Failed to authenticate with Vault")
        return self.client

    def get_secrets(self):
        """Retrieve secrets from Vault based on paths defined in a JSON file."""
        self.get_conn()
        secrets = {}
        with open(self.vault_secrets_file, 'r') as file:
            paths = json.load(file).get('secrets', [])
        for path in paths:
            secret = self.client.secrets.kv.v2.read_secret_version(path=path)
            secrets[path] = secret['data']['data']
        return secrets

