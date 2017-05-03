# Kubernetes Demo

All shell commands prefixed by `$` are executed locally on a dev machine without admin rights.

## Prerequisites

### Kubernetes cluster

For example, download [minikube](https://github.com/kubernetes/minikube/releases) utility and initiate the local cluster via:
```
$ ./minikube start
```
### kubectl

You need to install [kubectl](https://kubernetes.io/docs/user-guide/prereqs/) on your local machine and configure it to
work with the Kubernetes cluster.

For example, you can use:
```
$ brew install kubectl
```
If you use minikube, it automatically generates the `~/.kube/config` with the data similar to:
```
    apiVersion: v1


    clusters:
    - cluster:
      certificate-authority: /home/bookwar/.minikube/ca.crt
      server: https://192.168.99.100:8443
      name: minikube

    contexts:
    - context:
      cluster: minikube
      user: minikube
      name: minikube

    current-context: minikube

    kind: Config
    preferences: {}

    users:
    - name: minikube
      user:
        client-certificate: /home/bookwar/.minikube/apiserver.crt
        client-key: /home/bookwar/.minikube/apiserver.key
```

If you use a remote cluster, you need to create this file with proper server URL and user credentials.

Verify the configuration via running
```
$ kubectl cluster-info
Kubernetes master is running at https://192.168.99.100:8443
```
### Docker registry

You need a registry writable from local host and readable from the Kubernetes cluster. For example, DockerHub.

To be able to upload images to [DockerHub](https://hub.docker.com) you need to register as a user there and
login to the registry by running:
```
$ docker login
```

## Step 1: Application

In the real world container applications should work transparently and should not depend on a particular container. Thus
you would never rely on the local IP address or hostname of a container. But for the purpose of this demo we will use
application which exposes the container internals.

We create a very simple Python application which listens to the port 5000 and replies with the list of host ip
addresses.

### Create `./app.py`
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
### Build app

Come on, it is Python.

### Test app locally

Run it:
```
$ python app.py
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger pin code: 190-291-556
```
Access http://localhost:5000 to see the result:
```
$ wget -qO- http://localhost:5000
IP information:192.168.43.135 192.168.37.164 192.168.122.1 192.168.200.1
```
## Step 2: Container Image

### Create `./Dockerfile`

Starting from `fedora:latest` image, we install runtime dependencies, then copy our `app.py` application from host
into container, and then define container endpoint to run the command `python app.py` on start.
```
    FROM fedora:latest
    MAINTAINER Aleksandra Fedorova "alpha@bookwar.info"
    RUN dnf install -y python-flask hostname && dnf clean all
    COPY ./app.py /app/
    WORKDIR /app
    ENTRYPOINT ["python"]
    CMD ["app.py"]
```
### Build and tag the image:

Let's use name `local/my-ip` and version 0.0.1:
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

Tag it as bookwar/my-ip (bookwar is my user at DockerHUb)
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
