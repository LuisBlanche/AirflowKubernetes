from datetime import datetime, timedelta

import pandas as pd
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from kubernetes.client import models as k8s

default_args = {
    "owner": "dataswati",
    "start_date": days_ago(2),
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
} 

def get_volume_components(
    dag_id,
    host_path="/home/dev/Luis/odsc/AirflowKubernetes/dataswati/data",
    container_path="/tmp",
    volume_name="hostpath-volume",
):
    volume_data = k8s.V1Volume(name=volume_name, host_path=k8s.V1HostPathVolumeSource(path=host_path, type="Directory"))
    volume_mount_data = k8s.V1VolumeMount(
        mount_path=container_path, name=volume_name, read_only=False, sub_path=f"dag_{dag_id}",
    )
    return volume_data, volume_mount_data

dag_id = 'Aiflow_ML_k8s'

VOLUME_DATA, VOLUME_MOUNT_DATA = get_volume_components(dag_id=dag_id, container_path="/tmp")


resources = k8s.V1ResourceRequirements(requests={"memory": "1Gi", "cpu": "1",}, limits={"cpu": 2,},)
DATA_PATH = "/home/dev/Luis/odsc/AirflowKubernetes/dataswati/data"


with DAG(dag_id=dag_id, default_args= default_args, schedule_interval=None, max_active_runs=1) as dag:
    make_dataset = KubernetesPodOperator(task_id='make_dataset',
                                         trigger_rule='all_success', 
                                         namespace='default', 
                                         image="dataswatidevops/odsc_python_airflow_k8s:main",
                                         labels={"airflow": "operator"},
                                         name="airflow-operator-" + str(dag_id) + "-task",
                                         in_cluster=True,
                                         resources=resources,
                                         get_logs=True,
                                         is_delete_operator_pod=True,
                                         image_pull_policy="Always",
                                         cmds=[f"python -m potability/data/make_dataset.py {DATA_PATH}/raw {DATA_PATH}/interim"],
                                         volumes=[VOLUME_DATA],
                                         volume_mounts=[VOLUME_MOUNT_DATA],
                                         dag=dag,
                                         do_xcom_push=True
                                         ) 
    
