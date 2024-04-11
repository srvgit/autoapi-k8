from airflow.operators.python_operator import PythonOperator

def prepare_secret_volume():
    secrets = get_secrets()  # Assume get_secrets fetches your secrets
    with open('/path/to/secure/volume/secrets.txt', 'w') as f:
        for key, value in secrets.items():
            f.write(f'{key}={value}\n')

def cleanup_secret_volume():
    os.remove('/path/to/secure/volume/secrets.txt')

prepare_secrets = PythonOperator(
    task_id='prepare_secrets',
    python_callable=prepare_secret_volume,
    dag=dag
)

cleanup_secrets = PythonOperator(
    task_id='cleanup_secrets',
    python_callable=cleanup_secret_volume,
    trigger_rule='all_done',  # Ensures cleanup happens regardless of task success/failure
    dag=dag
)

docker_task = DockerOperator(
    task_id='docker_run_task',
    image='your_docker_image',
    volumes=['/path/to/secure/volume:/container/path'],
    command="run your command that reads secrets from /container/path/secrets.txt",
    dag=dag
)

prepare_secrets >> docker_task >> cleanup_secrets
