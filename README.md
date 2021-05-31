# AirflowKubernetes

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

Use the -f to override values in the official aiflow chart with [override_values.yaml](override_values.yaml). This will enable `git-sync` to allow airflow to get the dags from the [dags](dags) folder 

```
microk8s helm3 install airflow2 apache-airflow/airflow -f AirflowKubernetes/override_values.yaml
```


To access the Web UI => apply the port forwarding as indicated 

```
microk8s kubectl port-forward svc/airflow2-webserver 8080:8080 --namespace default
```



