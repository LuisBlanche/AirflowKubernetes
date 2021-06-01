from datetime import timedelta

from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

default_args = {
    "owner": "dataswati",
    "start_date": days_ago(2),
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}


def get_volume_components(
    dag_id,
    host_path="/home/dev/Luis/odsc/AirflowKubernetes/dataswati/data",  # PUT YOU OWN PATH HERE
    container_path="/app/data",
    volume_name="hostpath-volume",
):
    volume_data = k8s.V1Volume(name=volume_name, host_path=k8s.V1HostPathVolumeSource(path=host_path, type="Directory"))
    volume_mount_data = k8s.V1VolumeMount(
        mount_path=container_path,
        name=volume_name,
        read_only=False,
        sub_path=f"dag_{dag_id}",
    )
    return volume_data, volume_mount_data


dag_id = "Aiflow_ML_k8s"

VOLUME_DATA, VOLUME_MOUNT_DATA = get_volume_components(dag_id=dag_id, container_path="/tmp")


resources = k8s.V1ResourceRequirements(
    requests={
        "memory": "1Gi",
        "cpu": "1",
    },
    limits={
        "cpu": 2,
    },
)
DATA_PATH = "/app/data"


with DAG(dag_id=dag_id, default_args=default_args, schedule_interval=None, max_active_runs=1) as dag:
    make_dataset = KubernetesPodOperator(
        task_id="make_dataset",
        trigger_rule="all_success",
        namespace="default",
        image="dataswatidevops/odsc_python_airflow_k8s",
        labels={"airflow": "operator"},
        name="airflow-operator-" + str(dag_id) + "-task",
        in_cluster=True,
        resources=resources,
        get_logs=True,
        is_delete_operator_pod=True,
        image_pull_policy="Always",
        cmds=[f"python potability/data/make_dataset.py {DATA_PATH}"],
        volumes=[VOLUME_DATA],
        volume_mounts=[VOLUME_MOUNT_DATA],
        dag=dag,
        do_xcom_push=True,
    )

    impute_train_data = KubernetesPodOperator(
        task_id="make_dataset",
        trigger_rule="all_success",
        namespace="default",
        image="dataswatidevops/odsc_python_airflow_k8s",
        labels={"airflow": "operator"},
        name="airflow-operator-" + str(dag_id) + "-task",
        in_cluster=True,
        resources=resources,
        get_logs=True,
        is_delete_operator_pod=True,
        image_pull_policy="Always",
        cmds=[
            f"python potability/data/impute.py {{task_instance.xcom_pull(task_ids='make_dataset', key='return_values')['train_features_path]}} {DATA_PATH}/processed/train_features_imputed.csv"
        ],
        volumes=[VOLUME_DATA],
        volume_mounts=[VOLUME_MOUNT_DATA],
        dag=dag,
        do_xcom_push=True,
    )

    impute_unseen_data = KubernetesPodOperator(
        task_id="make_dataset",
        trigger_rule="all_success",
        namespace="default",
        image="dataswatidevops/odsc_python_airflow_k8s",
        labels={"airflow": "operator"},
        name="airflow-operator-" + str(dag_id) + "-task",
        in_cluster=True,
        resources=resources,
        get_logs=True,
        is_delete_operator_pod=True,
        image_pull_policy="Always",
        cmds=[
            f"python potability/data/impute.py {{task_instance.xcom_pull(task_ids='make_dataset', key='return_values')['unseen_features_path]}} {DATA_PATH}/processed/train_features_imputed.csv"
        ],
        volumes=[VOLUME_DATA],
        volume_mounts=[VOLUME_MOUNT_DATA],
        dag=dag,
        do_xcom_push=True,
    )


make_dataset >> [impute_train_data, impute_unseen_data]
