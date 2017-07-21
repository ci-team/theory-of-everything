---
slug: 16/kubernetes-demo
title: Kubernetes demo
author: bookwar
date: 1500663089366
tags: kubernetes
categories: Knowledge Base
link: https://quantum-integration.org/topic/16/kubernetes-demo
---

In this demo-like tutorial I am not going to explain how Kubernetes works. Instead I will show how *you* work with Kubernetes.

**Note:** All shell commands prefixed by `$` are executed locally on a dev machine without admin rights.

----
## Prerequisites

Things you need to setup to run through this tutorial:
* Kubernetes cluster
* kubectl command line tool
* Docker registry

### Kubernetes cluster

If you do not have a cluster available, download [minikube](https://github.com/kubernetes/minikube/releases) utility and initiate the local cluster via:
```
$ ./minikube start
```
It will fetch the virtual machine image with preconfigured one-node Kubernetes cluster and run it on your local machine.

### kubectl

You need to install [kubectl](https://kubernetes.io/docs/user-guide/prereqs/) on your local machine and configure it to work with the Kubernetes cluster you got in the prevous step.

For example on Fedora:
```
$ sudo dnf install kubernetes-client
```
kubectl reads its configuration from `~/.kube/config` file.

Minikube generates kubectl configuration file automatically. It should look similar to the following:
```
apiVersion: v1
kind: Config
preferences: {}

clusters:
    - cluster:
      certificate-authority: /home/bookwar/.minikube/ca.crt
      server: https://192.168.99.100:8443
      name: minikube

users:
    - name: minikube
      user:
        client-certificate: /home/bookwar/.minikube/apiserver.crt
        client-key: /home/bookwar/.minikube/apiserver.key

contexts:
    - context:
      cluster: minikube
      user: minikube
      name: minikube

current-context: minikube

```

If you use a remote cluster, you need to create or update this file manually with relevant credentials

Verify the configuration by running
```
$ kubectl cluster-info
Kubernetes master is running at https://192.168.99.100:8443
```
### Access to Docker registry

To work with containerized applications you need a registry of container images. In this tutorial we need to push images to the registry from dev machine and pull them from the cluster. While one can (and, I believe, should) setup private registry for this purpose, it is way out of scope for our simple tutorial.

Thus, in this tutorial we are going to use DockerHub, which is configured by default in minikube.

To be able to upload images to Docker Hub, sign up through its [web interface](https://hub.docker.com). Then login to the registry from local machine by running:
```
$ docker login 
```
----
## Ready?

Here is what we are going to do:
* write an application and test it,
* package it into a docker image, test it and publish to registry
* deploy the application to the Kubernetes cluster and test it,
* Roll out an update and, you get this by now, test it.

## Step 1: Application

Proper containerized applications should work transparently and should never depend on a particular container instance. Thus you would never rely on the local IP address or hostname of a container in real life. But for the purpose of this demo we will use application which exposes the container internals.

We create a very simple Python application which listens to the port *5000* and replies with the list of host ip addresses.

### Write

Create file `./app.py` with a Flask application :
```
from flask import Flask

import subprocess

app = Flask(__name__)

@app.route('/')
def hello():
    ip_a = subprocess.check_output([
        "hostname",
        "--all-ip-addresses"
    ]).split()
    return "IP information:" + " ".join(ip_a) + "\n"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
```
### Build

Oh, come on, it is Python.

### Test

Run it:
```
$ python app.py
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger pin code: 190-291-556
```
Access http://localhost:5000 to see it working:
```
$ wget -qO- http://localhost:5000
IP information:192.168.43.135 192.168.37.164 192.168.122.1 192.168.200.1
```
## Step 2: Container Image

### Create `./Dockerfile`

We start from `fedora:latest` image, install runtime dependencies, then copy our `app.py` application from the host
into container, and then define container endpoint to run the command `python app.py` on start.
```
FROM fedora:latest
MAINTAINER bookwar "alpha@bookwar.info"
RUN dnf install -y python-flask hostname && dnf clean all
COPY ./app.py /app/
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["app.py"]
```
### Build and tag the image:

Let's use name `local/my-ip` and version `0.0.1`:
```
$ docker build -t local/my-ip:0.0.1 .
```
### Test image

Run container locally
```
$ docker run -p 8888:5000 local/my-ip:0.0.1
```
Note that while application uses port 5000 inside the container, we link it to port 8888 on a host network.

Thus now we can access http://localhost:8888 and see the report with internal IP address of the container:
```
$ wget -qO- http://localhost:8888
IP information:172.17.0.2
```
### Push container to the registry.

Tag it as `bookwar/my-ip` (here `bookwar` is my user at DockerHub, use yours)
```
$ docker tag local/my-ip:0.0.1 bookwar/my-ip:0.0.1
```
Push to the registry
```
$ docker push bookwar/my-ip:0.0.1
```
Now image is available at DockerHUb and anyone can use it via the `bookwar/my-ip:0.0.1` name.

## Step 3: Deployment

### Create a deployment object

We call it `my-ip` and  set replica counter to 5 pods.
```
$ kubectl run --image=bookwar/my-ip:0.0.1 --replicas=5 my-ip
```
### Check that 5 pods were created:
```
$ kubectl get pods
NAME                     READY     STATUS    RESTARTS   AGE
my-ip-3794442940-1m52n   1/1       Running   0          3m
my-ip-3794442940-2642d   1/1       Running   0          3m
my-ip-3794442940-61lqf   1/1       Running   0          3m
my-ip-3794442940-97nx1   1/1       Running   0          3m
my-ip-3794442940-fdpvv   1/1       Running   0          3m
```
Pods are listening on the local network inside the cluster and are not accessible from the outside.

### Create an exposed service:
```
$ kubectl expose deployment my-ip --type=NodePort --name=my-ip-service --port 5000
```
### Find out the service node port

Now there is a service which redirects every request to it to port 5000 of a pod in the `my-ip` deployment group. This
service has type `NodePort`, which means that it is exposed as a port on every cluster node. To find our the exact value
of a NodePort, we can check the service details via `describe` subcommand.
```
$ kubectl describe service my-ip-service
Name: my-ip-service
Namespace: default
...
NodePort: <unset> 30346/TCP
...
```
Note the 30346 NodePort assigned to the service.

### Check the service

Now it is easy to reach service from the outside via NodePort by accessing the http://192.168.99.100:30346
```
$ wget -qO- http://192.168.99.100:30346
IP information: 172.17.0.4
```
Here we use the same IP which we got from running `kubectl cluster-info` command.

### Let us also test it with the debugging pod

Run the pod:
```
$ kubectl run -i --tty busybox --image=busybox --rm --restart=Never
```
Using shell prompt inside the pod call the service via command line several times:
```
# / wget -qO- my-ip-service.default:5000
IP information: 172.17.0.4
# / wget -qO- my-ip-service.default:5000
IP information: 172.17.0.6
```
Note that we are using the DNS name and internal port 5000 as we work with internal cluster network.

You also get different IP addresses in response, as requests get balanced to different pods behind the service.

## Step 4: Rolling out an update

Deployment objects in Kubernetes come with the update strategy. By default, it is set to RollingUpdate.
```
$ kubectl describe deployment my-ip
Name:      my-ip
 ...
StrategyType:    RollingUpdate
RollingUpdateStrategy:  1 max unavailable, 1 max surge
 ...
```
Let's update the base container image for our `my-ip` pods.

### Edit the `app.py`

We add the "Hello world!" string:
```
    from flask import Flask

    import subprocess

    app = Flask(__name__)

    @app.route('/')
    def hello():
        ip_a = subprocess.check_output([
            "hostname",
            "--all-ip-addresses"
        ]).split()
        return "Hello, world! Here is my IP information: " + " ".join(ip_a) + "\n"

    if __name__ == '__main__':
        app.run(debug=True,host='0.0.0.0')
```
### Build, tag and push new 0.0.2 version of the image
```
$ docker build -t local/my-ip:0.0.2 .
$ docker tag bookwar/my-ip:0.0.2 local/my-ip:0.0.2
$ docker push bookwar/my-ip:0.0.2
```
### Bump version of an image used in deployment object

Image version is stored in the configuration of our deployment object. There are several ways to change it, let's
use the intercative edit of a deployment:
```
$ kubectl edit deployment my-ip
```
Running the command will open the editor with a yaml configuration of a `my-ip` deployment. Find the container spec
block and edit the image version:
```
       spec:
         containers:
         - image: bookwar/my-ip:2.0.0
```
  Save and exit. The rollout procedure will start immediately.

### Verify the update

Call the service via external port again:
```
$ wget -qO- http://192.168.99.100:30346
Hello, world! My IP information: 172.17.0.8
```
New version is rolled out and we got a different string.

