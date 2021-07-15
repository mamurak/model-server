# Deploying a machine learning model with OpenShift Serverless Functions.
![Iris Data Set](/images/iris.jpg "Iris Data Set")

This project is a simple example on how to deploy a machine learning model using OpenShift Serverless Functions. 
It is based on a SciKit Learn Random Forest Classifier model that is trained using R.A. Fisher's famous [Iris data set](https://archive.ics.uci.edu/ml/datasets/iris).

#### The Server

The server takes care of loading the ML model, preparing the incoming data, calling the model predictor and returning the prediction to the client.

It consists of a python program `func.py`, which runs in a container when the pod gets scheduled. The program contains the `main()` 
serverless function, which gets invoked when an http request is received. Code outside of `main()` gets loaded once when the pod runs and can be considered in global scope. 
Code inside of `main()` is invoked each time an http request is made and contains a new context object.

#### The Client
An example Jupyter notebook client program `01-iris-rest-client.ipynb`, that makes REST calls to the serverless service.

#### The Setup

- Fedora 34
  - `podman` to build and run containers.
  - A container registry (local, quay.io, docker.io, OpenShift) with write privs. 
  - The knative `kn` binary with the `func` plugin. (See the [manual config](#manual-configuration) section)
  - Developer access to an OpenShift 4.7 cluster with Serverless support.

#### How to build, deploy and serve the model in this repo.
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

2) Use `podman` to login to the registry and create an auth file to cache credentials. 
```
podman login --authfile $HOME/.docker/config.json reg.redhatgov.io:5000
```

3) Login to an OpenShift cluster with serverless support.

If an external registry that requires authentication is being used, create and link a secret so OpenShift can pull images from it. 
```
oc create secret docker-registry reg.redhatgov.io --docker-server=reg.redhatgov.io:5000 --docker-username=redhat --docker-password=password
```
```
oc secrets link default reg.redhatgov.io --for=pull
```

4) Build and create the image. This example uses a private registry.
```
kn func build --image=reg.redhatgov.io:5000/redhat/myfunc:latest
```

5) Run the container.

```
kn func run
```

The container could also be run from directly from `podman`.
```
podman run --rm --name=model-server -p8080:8080 -d reg.redhatgov.io:5000/redhat/model-server:latest
```

6) Test locally by sending data with a `curl`.

```
curl -X POST -H "Content-Type: application/json" --data '{"sl": 5.9, "sw": 3.0, "pl": 5.1, "pw": 1.8}' http://127.0.0.1:8080
```


7) Finally, deploy to OpenShift via private registry.

```
kn func deploy
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
#### Autoscaling

1) Get the service name.
```
kn service list
```
2) Update the autoscale parameters with unusually low values.
```
kn service update <service-name> --concurrency-limit=1 --concurrency-target=1 --concurrency-utilization=30
```
3) Curl the endpoint a few times and it should trigger a number pods to run.

4) To change the autoscale window use `--autoscale-window=90s`

#### Manual Configuration
1) Download the [kn binary](https://github.com/knative/client/tags), `chmod u+x` and place it in `$PATH`.
```
chmod u+x kn-linux-amd64
mv kn-linux-amd64 $HOME/.local/bin/kn
```

2) Make the plugin directory
```
mkdir $HOME/.config/kn/plugins
```

3) [Download](https://github.com/knative-sandbox) your favorite plugins and install them in `$HOME/.config/kn/plugins`.
```
chmod u+x func_linux_amd64
mv func_linux_amd64 
$HOME/.config/kn/plugins/kn-func
```

4) Verify
```
kn plugin list
```
```
- kn-admin : /home/koz/.config/kn/plugins/kn-admin
- kn-func : /home/koz/.config/kn/plugins/kn-func
```

#### Troubleshooting

- `/tmp` and `podman` can run out of free space.
- Don't use port 8080 for the `podman` API service or it will conflict with `kn func run`.


#### Creating a serverless function from scratch.
```
mkdir functions
```
```
kn func create --runtime=python functions/myfunc
```

Build, run and deploy the same as above.

#### Reference

[Openshift serverless docs](https://docs.openshift.com/container-platform/4.7/serverless/functions/serverless-functions-about.html)
