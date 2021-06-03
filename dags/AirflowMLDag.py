from datetime import timedelta
from typing import List

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
    host_path="/home/dev/Luis/odsc/AirflowKubernetes/dataswati/data",  # PUT YOU OWN PATH HERE
    container_path="/app/data",
    volume_name="hostpath-volume",
):
    volume_data = k8s.V1Volume(name=volume_name, host_path=k8s.V1HostPathVolumeSource(path=host_path, type="Directory"))
    volume_mount_data = k8s.V1VolumeMount(
        mount_path=container_path,
        name=volume_name,
        read_only=False,
    )
    return volume_data, volume_mount_data


dag_id = "Airflow_ML_k8s"
HOST_PATH = "home/dev/Luis/odsc/AirflowKubernetes/dataswati"

VOLUME_DATA, VOLUME_MOUNT_DATA = get_volume_components(f"{HOST_PATH}/data")
VOLUME_MODELS, VOLUME_MOUNT_MODELS = get_volume_components(f"{HOST_PATH}/models")


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
MODELS_PATH = "/app/models"
N_ITER = "10"
N_CV = "3"
N_JOBS = "4"


def WrapperKubernetesPodOperator(
    dag,
    task_id: str,
    cmds: List[str],
    do_xcom_push: bool = True,
):
    return KubernetesPodOperator(
        task_id=task_id,
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
        cmds=cmds,
        volumes=[VOLUME_DATA, VOLUME_MODELS],
        volume_mounts=[VOLUME_MOUNT_DATA, VOLUME_MOUNT_MODELS],
        dag=dag,
        do_xcom_push=do_xcom_push,
        startup_timeout_seconds=200,
    )


with DAG(dag_id=dag_id, default_args=default_args, schedule_interval=None, max_active_runs=1) as dag:

    make_dataset = WrapperKubernetesPodOperator(
        task_id="make_dataset",
        cmds=["python", "/app/potability/data/make_dataset.py", DATA_PATH],
        dag=dag,
        do_xcom_push=True,
    )

    impute_train_data = WrapperKubernetesPodOperator(
        task_id="impute_train_data",
        cmds=[
            "python",
            "/app/potability/data/impute.py",
            "{{ task_instance.xcom_pull(task_ids='make_dataset', key='return_value')['train_features_path'] }}",
            f"{DATA_PATH}/processed/train_features_imputed.csv",
        ],
        dag=dag,
        do_xcom_push=True,
    )

    impute_unseen_data = WrapperKubernetesPodOperator(
        task_id="impute_unseen_data",
        cmds=[
            "python",
            "/app/potability/data/impute.py",
            "{{ task_instance.xcom_pull(task_ids='make_dataset',  key='return_value')['unseen_features_path'] }}",
            f"{DATA_PATH}/processed/unseen_features_imputed.csv",
        ],
        dag=dag,
        do_xcom_push=True,
    )

    build_train_features = WrapperKubernetesPodOperator(
        task_id="build_train_features",
        cmds=[
            "python",
            "/app/potability/features/build_features.py",
            "{{ task_instance.xcom_pull(task_ids='impute_train_data', key='return_value')['imputed_path'] }}",
            f"{DATA_PATH}/processed/train_features.csv",
        ],
        dag=dag,
        do_xcom_push=True,
    )

    build_unseen_features = WrapperKubernetesPodOperator(
        task_id="build_unseen_features",
        cmds=[
            "python",
            "/app/potability/features/build_features.py",
            "{{ task_instance.xcom_pull(task_ids='impute_unseen_data', key='return_value')['imputed_path'] }}",
            f"{DATA_PATH}/processed/unseen_features.csv",
        ],
        dag=dag,
        do_xcom_push=True,
    )

    train_rf = WrapperKubernetesPodOperator(
        task_id="train_rf",
        cmds=[
            "python",
            "/app/potability/models/train_model.py",
            "rf",
            "{{ task_instance.xcom_pull(task_ids='build_train_features', key='return_value')['features_path'] }}",
            "{{ task_instance.xcom_pull(task_ids='make_dataset', key='return_value')['train_target_path'] }}",
            MODELS_PATH,
            N_ITER,
            N_JOBS,
            N_CV,
        ],
        dag=dag,
        do_xcom_push=False,
    )
    train_interpret = WrapperKubernetesPodOperator(
        task_id="train_interpret",
        cmds=[
            "python",
            "/app/potability/models/train_model.py",
            "interpret",
            "{{ task_instance.xcom_pull(task_ids='build_train_features', key='return_value')['features_path'] }}",
            "{{ task_instance.xcom_pull(task_ids='make_dataset', key='return_value')['train_target_path'] }}",
            MODELS_PATH,
            N_ITER,
            N_JOBS,
            N_CV,
        ],
        dag=dag,
        do_xcom_push=False,
    )
    train_lgbm = WrapperKubernetesPodOperator(
        task_id="train_lgbm",
        cmds=[
            "python",
            "/app/potability/models/train_model.py",
            "lightgbm",
            "{{task_instance.xcom_pull(task_ids='build_train_features', key='return_value')['features_path']}}",
            "{{task_instance.xcom_pull(task_ids='make_dataset', key='return_value')['train_target_path']}}",
            MODELS_PATH,
            N_ITER,
            N_JOBS,
            N_CV,
        ],
        dag=dag,
        do_xcom_push=False,
    )

    predict_rf = WrapperKubernetesPodOperator(
        task_id="predict_rf",
        cmds=[
            "python",
            "/app/potability/models/predict_model.py",
            "{{ task_instance.xcom_pull(task_ids='build_unseen_features', key='return_value')['features_path'] }}",
            "{{ task_instance.xcom_pull(task_ids='make_dataset', key='return_value')['unseen_target_path'] }}",
            f"{DATA_PATH}/processed/rf_predictions.csv",
            f"{MODELS_PATH}/rf/potability.joblib" "rf",
        ],
        dag=dag,
        do_xcom_push=False,
    )
    predict_interpret = WrapperKubernetesPodOperator(
        task_id="predict_interpret",
        cmds=[
            "python",
            "/app/potability/models/predict_model.py",
            "{{ task_instance.xcom_pull(task_ids='build_unseen_features', key='return_value')['features_path'] }}",
            "{{ task_instance.xcom_pull(task_ids='make_dataset', key='return_value')['unseen_real_target'] }}",
            f"{DATA_PATH}/processed/interpret_predictions.csv",
            f"{MODELS_PATH}/interpret/potability.joblib",
        ],
        dag=dag,
        do_xcom_push=False,
    )
    predict_lgbm = WrapperKubernetesPodOperator(
        task_id="predict_lgbm",
        cmds=[
            "python",
            "/app/potability/models/predict_model.py",
            "{{ task_instance.xcom_pull(task_ids='build_unseen_features', key='return_value')['features_path'] }}",
            "{{ task_instance.xcom_pull(task_ids='make_dataset', key='return_value')['unseen_real_target'] }}",
            f"{DATA_PATH}/processed/lightgbm_predictions.csv",
            f"{MODELS_PATH}/lightgbm/potability.joblib",
        ],
        dag=dag,
        do_xcom_push=False,
    )


make_dataset >> [impute_train_data, impute_unseen_data]
impute_train_data >> build_train_features
impute_unseen_data >> build_unseen_features
build_train_features >> [train_rf, train_interpret, train_lgbm]
[train_rf, build_unseen_features] >> predict_rf
[train_interpret, build_unseen_features] >> predict_interpret
[train_lgbm, build_unseen_features] >> predict_lgbm
