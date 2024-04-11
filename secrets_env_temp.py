from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from hooks.vault_hook import VaultHook

def get_secrets():
    hook = VaultHook('aws_secret_name_for_vault', '/path/to/vault_secrets.json')
    return hook.get_secrets()

def setup_docker_task(**kwargs):
    secrets = kwargs['ti'].xcom_pull(task_ids='get_secrets_task')
    env_vars = {key: val for key, val in secrets.items()}

    docker_task = DockerOperator(
        task_id='docker_run_task',
        image='your_docker_image',
        api_version='auto',
        auto_remove=True,
        environment=env_vars,
        network_mode="bridge",
        docker_url="unix://var/run/docker.sock",
        command="your command here",
        dag=kwargs['dag']
    )
    docker_task.execute(context=kwargs)

with DAG('docker_secrets_dag',
         start_date=datetime(2021, 1, 1),
         schedule_interval='@daily',
         catchup=False) as dag:

    get_secrets_task = PythonOperator(
        task_id='get_secrets_task',
        python_callable=get_secrets,
        provide_context=True
    )

    setup_docker_task = PythonOperator(
        task_id='setup_docker_task',
        python_callable=setup_docker_task,
        provide_context=True
    )

    get_secrets_task >> setup_docker_task
