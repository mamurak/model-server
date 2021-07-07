# Deploying a machine learning model with OpenShift Serverless Functions.
## My notes

### My setup

- Fedora 34
  - `podman` is needed to build images.
  - A container registry (local, quay.io, docker.io, OpenShift) with write privs. 
  - The [`func` binary](https://github.com/boson-project/func/tags)
  - Developer access to an OpenShift 4.7 cluster with Serverless support.

1a) Start the podman API service as a rootless user.

```
podman system service --time=0 tcp:0.0.0.0:8080
```
```
export DOCKER_HOST=tcp://127.0.0.1:8080
```

1b) Or use UNIX sockets.

```
systemctl --user enable --now podman.socket
```

```
export DOCKER_HOST="unix:///run/user/$(id -u)/podman/podman.sock"
```

2) Download the [`func` binary](https://github.com/boson-project/func/tags) and install it
in `$PATH`.

- Make sure `/tmp` has ~512MB of free space.

3) Use `podman` to login to the registry and create an auth file to cache credentials. 
```
podman login --authfile $HOME/.docker/config.json reg.redhatgov.io:5000
```

4a) Login to an OpenShift cluster with serverless support.

4b) If using an external registry that requires authentication, create and link a secret so OpenShift can pull images from it. 
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

6a) Run the container.

```
func run
```

6b) At this point, the container could be run from `podman`.
```
podman run --rm --name=model-server -p8081:8080 -d reg.redhatgov.io:5000/redhat/model-server:latest
```

7) Finally, deploy to OpenShift via private registry.

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
