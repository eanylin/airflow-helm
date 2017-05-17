"""
Code that goes along with the Airflow tutorial located at:
https://github.com/airbnb/airflow/blob/master/airflow/example_dags/tutorial.py
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2017, 5, 16),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2017, 5, 16),
}

dag = DAG('test_dag', default_args=default_args, schedule_interval=None)

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag)

t2 = BashOperator(
    task_id='sleep',
    bash_command='sleep 5',
    retries=3,
    dag=dag)

templated_command = """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
        echo "{{ params.my_param }}"
    {% endfor %}
"""

t3 = BashOperator(
    task_id='templated',
    bash_command=templated_command,
    params={'my_param': 'Parameter I passed in'},
    dag=dag)

t_docker = DockerOperator(
    api_version='1.19',
    docker_url='unix:///var/run/docker.sock',  # replace it with swarm/docker endpoint
    image='kolla/ubuntu-source-kolla-toolbox:3.0.3',
    network_mode='bridge',
    volumes=['/home/ubuntu/workbench/dags:/dags'],
    command='openstack --version',
    task_id='get_projects',
    xcom_push=True,
    params={'source_location': '/your/input_dir/path',
         'target_location': '/your/output_dir/path'},
    dag=dag)

t2.set_upstream(t1)
t3.set_upstream(t1)

