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
microk8s enable helm3
```
```
microk8s helm init --stable-repo-url https://charts.helm.sh/stable
``` 



### 1.4 Create a Kubernetes secret with your github credentials 
```
echo -n 'admin' | base64
YWRtaW4=
echo -n '1f2d1e2e67df' | base64
MWYyZDFlMmU2N2Rm
```
Retrieve your base64 encoded credentials and insert them in [git-credentials.template](git-credentials.template) then change the name of this file : 
```
mv git_credentials.template git_credentials.yaml
```
Create the secret with `kubectl` : 

```
microk8s kubectl apply -f git-credentials.yaml
```
Check that the secret is created: 

```
microk8s kubectl  describe secret/git-credentials
```

Which should return something like this : 

```
Name:         git-credentials
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
GIT_SYNC_USERNAME:  21 bytes
GIT_SYNC_PASSWORD:  13 bytes
```


### 1.5 Airflow installation on Kubernetes

retrieve the airflow repository 

```
git clone https://github.com/apache/airflow
``` 

Go inside the repo and check the `chart` folder 

You can directly modify the `values.yaml` with advanced configurations.
Deactivate Arflow authentication for easier local development 

```
    webserverConfig: |

      import os
      from flask_appbuilder.security.manager import AUTH_DB
      AUTH_ROLE_PUBLIC = 'Admin'

      basedir = os.path.abspath(os.path.dirname(__file__))

      WTF_CSRF_ENABLED = True
      AUTH_TYPE = AUTH_DB
```

And 

```
    config:
    ...
      webserver:
        enable_proxy_fix: 'True'
        authenticate: 'False'
        rbac: 'False'
```

Enable Git Sync to find the Dags 
```
    gitSync:
      enabled: true
      ...
      repo: https://gitlab.com/dataswati-datascience/powerop-ai.git
      branch: "dev"
      rev: HEAD
      root: "/git"
      dest: "repo"
      ...
      subPath: "dags"                       # subdir were dags are stored
      ..
      credentialsSecret: git-credentials    # k8s secret name
```

**EASY Alternative** :  you can just retrieve the `values.yaml`  from this repo and replace it directly into the airflow chart


1.6 Run the Helm Chart 

```
microk8s helm3 install airflow2 chart
```

To access the Web UI => apply the port forwarding as indicated 

```
microk8s kubectl port-forward svc/airflow2-webserver 8080:8080 --namespace default
```



