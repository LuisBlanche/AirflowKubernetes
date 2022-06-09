# Build an ML Pipeline with Airflow and Kubernetes 
**This work is supported by [Dataswati](https://www.dataswati.com/)**

## Introduction 
This repo was designed for ODSC Europe Workshop : [Build an ML Pipeline with Airflow and Kubernetes](https://staging6.odsc.com/speakers/build-an-ml-pipeline-with-airflow-and-kubernetes/)

### What's in there 
All the code material for the workshop : 

* The ml code is in the [dataswati](dataswati) folder and is about fitting a water Potability classifier using a [dataset from Kaggle](https://www.kaggle.com/adityakadiwal/water-potability) 
* The airflow Dag code is it the [dags](dag) folder (we activate airflow git-sync to retrieve this code) 
* The [Dockerfile](Dockerfile) to build the image that is used by the KubernetesPodOperator and synchronized with [Docker Hub](https://hub.docker.com/repository/docker/dataswatidevops/odsc_python_airflow_k8s)
* [override_values.yaml](override_values.yaml) allows to override the [airflow helm chart](https://github.com/apache/airflow/tree/main/chart) to activate git-sync with the dag folder 



## 1. Installation 

### 1.1 Install lightweight version of Kubernetes : [microk8s](https://microk8s.io/)

LINUX 

```
sudo snap install microk8s --classic
``` 

```
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
su - $USER
```

WINDOWS 

[Download installer here](https://github.com/ubuntu/microk8s/releases/download/installer-v2.0.0/microk8s-installer.exe) and follow instructions

MACOS

```
brew install ubuntu/microk8s/microk8s
```

```
microk8s install
```



### 1.2 Test installation 

```
microk8s status --wait-ready
```



### 1.3 Helm configuration 

Helm is the package manager for kubernetes 

```
microk8s enable helm3 dns storage
```
```
microk8s helm init --stable-repo-url https://charts.helm.sh/stable
``` 



### 1.4 Airflow installation on Kubernetes
See the [doc for official airflow Helm chart](https://airflow.apache.org/docs/helm-chart/stable/index.html)

Use the -f to override values in the official aiflow chart with [override_values.yaml](override_values.yaml). This will enable `git-sync` to allow airflow to get the dags from the [dags](dags) folder 

```
microk8s helm3 repo add apache-airflow https://airflow.apache.org 
```


```
microk8s helm3 install airflow2 apache-airflow/airflow -f AirflowKubernetes/override_values.yaml
```



To access the Web UI => apply the port forwarding as indicated 

```
microk8s kubectl port-forward svc/airflow2-webserver 8080:8080 --namespace default
```

You can now access to the [Airflow UI](localhost:8080) where you will see the DAG  

### 1.5 Last **important** step : set you host path as an Airflow Variable

Go to Admin => Variable and create a variable called `HOST_PATH` with the path to you dataswati folder (eg: `/home/Luis/dev/odsc/AirflowKubernetes/dataswati`)

This will be important to determine where on your computer the volumes will be synced with 

## 2. Machine Learning  

## 2.1 Airflow DAG 
![image](https://user-images.githubusercontent.com/18741447/120769392-5d998e00-c51d-11eb-8c65-52580d199282.png)

Typical Machine Learning Pipeline : there is training data and unseen data, both dataset go through the same transformations (imputation and feature engineering) and then the training data is used for training different models with random hyperparameter search with crossvalidation only the best model of each type is kept and they are use to make a prediction on the unseen data (at the same time we can evaluate the predictions because we actually have the targets for the unseen data) 


## 2.2 ML Code 

This part of the repository was generated using [Coookiecutter Datascience](https://drivendata.github.io/cookiecutter-data-science/) that allows scaffolding of a data science project in a matter of minutes and brings cool functionalities with a lot of helpers. 
The code is split into 3 submodules : 
* [data](dataswati/potability/data) where we treat the existing data,
* [features](dataswati/potability/features) where we add new features to the data
* [models](dataswati/potability/models) where we create and train ML models and use them for prediction. 


## 2.3 The dataset 

Here we use a dataset from Kaggle : [Water Potability](https://www.kaggle.com/adityakadiwal/water-potability). The advantage is to have access to the notebooks on Kaggle that give a baseline for prediction score and cool EDAs, you can also access a pandas profiling report and a pycaret tests in the [exploration notebook](notebooks/exploration.html) 

