# Filename: dags/example_vault_dag.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from hooks.vault_hook import VaultHook

def fetch_and_print_secrets():
    # Assuming AWS secret and JSON file paths are correctly set
    hook = VaultHook('aws_secret_name_for_vault', '/path/to/vault_secrets.json')
    secrets = hook.get_secrets()
    for path, secret in secrets.items():
        print(f"Secrets from {path}: {secret}")

with DAG('vault_secrets_example_dag', start_date=datetime(2021, 1, 1), schedule_interval='@daily') as dag:
    retrieve_and_print_secrets_task = PythonOperator(
        task_id='retrieve_and_print_secrets',
        python_callable=fetch_and_print_secrets
    )
