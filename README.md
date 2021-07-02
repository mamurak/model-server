# Serverless/KNative Functions

## Notes

This example builds and pushes to a local registry running on Fedora 34. The OpenShift registry can also be exposed and used.

Start the podman service as a rootless user.

```
export DOCKER_HOST=tcp://127.0.0.1:8080
```
```
podman system service --time=0 tcp:0.0.0.0:8080
```

Download [`func` binary](https://github.com/boson-project/func/tags).

Make sure `/tmp` has free space.

Login to podman and optionally save the auth credentials. This is needed for the knative client to push to a registry. 
RHEL8 saves the creds in `$HOME/.config/containers/auth.json` but other OS's (like Fedora) may not.
```
$ podman login --authfile $HOME/.docker/config.json registry-url
```

Login to an OpenShift cluster with serverless support.

Create pull secrets so OpenShift can pull from an external registry.

```
oc create secret docker-registry reg.redhatgov.io --docker-server=reg.redhatgov.io:5000 --docker-username=redhat --docker-password=password

oc secrets link default reg.redhatgov.io --for=pull
```

```
$ mkdir functions

$ func create --runtime=python functions/myfunc
```

Build and create the image. This example uses a private registry.
```
$ cd functions/myfunc

$ func build --image=reg.redhatgov.io:5000/redhat/myfunc:latest
```

Deploy to OpenShift via private registry.

```
$ func deploy

...
...
...
🕒 Deploying function to the cluster
   Function deployed at URL: http://myfunc-functions.apps.shared-na46.openshift.opentlc.com
```

Test with `curl`.

```
$ curl http://myfunc-functions.apps.shared-na46.openshift.opentlc.com

{"message":"Howdy!"}
```

Send data with a `curl` POST.

```
$ curl -X POST -H "Content-Type: application/json" -d "mydata":"30" http://myfunc3-functions.apps.shared-na46.openshift.opentlc.com
```
