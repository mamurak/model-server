# Deploying a machine learning model with OpenShift Serverless Functions.

### My setup

- Fedora 34
  - `podman` to build images.
  - A container registry (local, quay.io, docker.io, OpenShift) with write privs. 
  - The [`func` binary](https://github.com/boson-project/func/tags)
  - Developer access to an OpenShift 4.7 cluster with Serverless support.

1) Start the podman API service as a rootless user. 

```
podman system service --time=0 tcp:0.0.0.0:1234
```
```
export DOCKER_HOST=tcp://127.0.0.1:1234
```

Or use UNIX sockets.

```
systemctl --user enable --now podman.socket
```

```
export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
```

2) Download the [`func` binary](https://github.com/boson-project/func/tags) and install it
in `$PATH`.

3) Use `podman` to login to the registry and create an auth file to cache credentials. 
```
podman login --authfile $HOME/.docker/config.json reg.redhatgov.io:5000
```

4) Login to an OpenShift cluster with serverless support.

If an external registry that requires authentication is being used, create and link a secret so OpenShift can pull images from it. 
```
oc create secret docker-registry reg.redhatgov.io --docker-server=reg.redhatgov.io:5000 --docker-username=redhat --docker-password=password
```
```
oc secrets link default reg.redhatgov.io --for=pull
```

5) Build and create the image. This example uses a private registry.
```
func build --image=reg.redhatgov.io:5000/redhat/myfunc:latest
```

6) Run the container.

```
func run
```

The container could also be run from directly from `podman`.
```
podman run --rm --name=model-server -p8080:8080 -d reg.redhatgov.io:5000/redhat/model-server:latest
```

7) Test locally by sending data with a `curl`.

```
curl -X POST -H "Content-Type: application/json" --data '{"sl": 5.9, "sw": 3.0, "pl": 5.1, "pw": 1.8}' http://127.0.0.1:8080
```


8) Finally, deploy to OpenShift via private registry.

```
func deploy
```
```
...
...
...
🕒 Deploying function to the cluster
   Function deployed at URL: http://myfunc-functions.apps.shared-na46.openshift.opentlc.com
```

Send data with a `curl` POST.

```
curl -X POST -H "Content-Type: application/json" --data '{"sl": 5.9, "sw": 3.0, "pl": 5.1, "pw": 1.8}' http://model-server-functions.apps.shared-na46.openshift.opentlc.com
```

#### Troubleshooting

- `/tmp` and `podman` can run out of free space.
- Don't use port 8080 for the `podman` API service or it will conflict with `func run`.

### Autoscaling

1) To force autoscaling, first install the `kn` binary.
2) Get the service name.
```
kn service list
```
3) Update the autoscale parameters with unusually low values.
```
kn service update <service-name> --concurrency-limit=1 --concurrency-target=1 --concurrency-utilization=30
```
4) Curl the endpoint a few times and it should trigger a number pods to run.

### Creating a serverless function from scratch.
```
mkdir functions
```
```
func create --runtime=python functions/myfunc
```

Build
```
func build --image=reg.redhatgov.io:5000/redhat/myfunc:latest
```

Deploy
```
func deploy
```
Test

```
curl http://myfunc-functions.apps.shared-na46.openshift.opentlc.com
```
```
{"message":"Howdy!"}
```

#### Reference

[Openshift serverless docs](https://docs.openshift.com/container-platform/4.7/serverless/functions/serverless-functions-about.html)
