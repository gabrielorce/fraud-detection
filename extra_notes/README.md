
## Registry - Image Pull Policy

By default, if ```imagePullPolicy``` is omitted in a Deployment manifest, Kubernetes applies a default rule based on the image tag:

- If the tag is ```:latest``` (e.g., ```local-registry/fraud-frontend:latest```), then Kubernetes defaults ```imagePullPolicy``` to ```Always```.  

- If the tag is anything else (e.g., ```:v1.0.0```), Kubernetes defaults it to ```IfNotPresent```.  


## Kind/Minikube specific:

When using locally built images with Kind or Minikube, make sure your Deployment spec (or your ```values.yaml``` setting) uses:

```imagePullPolicy: IfNotPresent # or Never```


If it is set to ```Always```, Kubernetes will try to reach out to the internet to pull ```local-registry/fraud-frontend:```latest from a public server, ignore your local image, and throw an ```ImagePullBackOff``` or ```ErrImagePull``` error. See below example:


```$ kubectl get pods -w

NAME                                READY   STATUS              RESTARTS   AGE
frontend-ui-654c744f67-xg9d7        0/1     ErrImagePull        0          8s
ml-fraud-service-74b56b6695-dd4zm   0/1     Init:0/1            0          8s
ml-fraud-service-74b56b6695-tm9dk   0/1     Init:0/1            0          8s
postgres-0                          0/1     ContainerCreating   0          8s
postgres-0                          1/1     Running             0          13s
ml-fraud-service-74b56b6695-tm9dk   0/1     Init:0/1            0          14s
frontend-ui-654c744f67-xg9d7        0/1     ImagePullBackOff    0          16s
ml-fraud-service-74b56b6695-dd4zm   0/1     PodInitializing     0          31s
frontend-ui-654c744f67-xg9d7        0/1     ErrImagePull        0          33s
```


If pods are still stuck, inspect the exact error message:   
```kubectl describe pod <pod-name-from-kubectl-get-pods>```  

Scroll down to the Events section at the bottom. It will tell you line-by-line whether it's looking for a remote host or missing the tag.

## Helm Notes
  
Without Helm, you write static ```deployment.yaml``` and ```service.yaml``` files and apply them directly with ```kubectl apply -f```.
  
With Helm:
- You put those same kinds of YAML files inside a chart's templates/ folder (e.g. ```templates/deployment.yaml```, ```templates/service.yaml```)
- Instead of hardcoding values, you use template syntax to pull from a values.yaml file, like ```{{ .Values.image.repository }}``` or ```{{ .Values.replicaCount }}```
- Helm renders those templates into real Kubernetes manifests and applies them for you, tracking the result as a "release"
  

ANOTHER TOPIC:  
See ```templates/ml-configmap.yaml```:
Helm dynamically pulls in the full python script at deploy time using ```.Files.Get```
See:
https://helm.sh/docs/chart_template_guide/accessing_files/


