
## Kubernetes InitContainer (Automated inside cluster)


<https://kubernetes.io/docs/concepts/workloads/pods/init-containers/>   
A lightweight initContainer is added to the ML Service deployment (```templates/ml-deployment.yaml```). Before the  FastAPI service boots, the init container runs this training script and writes ```fraud_model.pkl``` directly to the shared PVC volume.   
   
To run the training script automatically on Pod startup, we add an initContainers array to the ml-deployment.yaml spec.

The initContainer runs to completion before the main FastAPI container starts. It mounts the exact same PVC volume (```ml-data-volume```), executes `train_model.py`, saves ```fraud_model.pkl``` to ```/mnt/data```, and exits. Then, the main container boots up and loads the fresh model immediately.

To inject ```train_model.py``` into the Kubernetes cluster without building a separate Docker image for training, we wrap the script inside a Helm ConfigMap.    
   
Execution Flow:   



```
1. Pod Scheduled on Node  
   │  
   ▼  
2. Executing initContainer: 'model-trainer'  
   ├── Mounts PVC to /mnt/data  
   ├── Mounts ConfigMap to /scripts/train_model.py  
   ├── Executes: python /scripts/train_model.py  
   └── Writes: /mnt/data/fraud_model.pkl  
   │  
   ▼ (InitContainer exits with status 0)  
3. Starting Main Container: 'ml-api'  
   ├── Mounts PVC to /mnt/data  
   └── Reads: /mnt/data/fraud_model.pkl on startup    
```

## Use of Readiness Probe
Without a Readiness Probe, Kubernetes will send traffic from the frontend-ui to ml-service as soon as the container boots up. If scikit-learn takes a few seconds to load fraud_model.pkl into memory, early requests will crash with 500 Internal Server Error    
This is defined in the ```ml-deployment.yaml```  file.   


## NOTE - In Kubernetes:    
***Sidecar container*** are containers that start before the main application container and continue to run.    
***Init containers***: containers that run to completion during Pod initialization. Init-containers are used to initialize something inside your Pod. The init-containers will run and exit. After every init container which exits with a code 0, your main containers will start.      
   
     

***GIVE EXAMPLES***
   
## ConfigMaps 
<https://kubernetes.io/docs/concepts/configuration/configmap/>      
<https://helm.sh/docs/chart_template_guide/getting_started/>    
A ConfigMap allows you to decouple environment-specific configuration from your container images, so that your applications are easily portable.     


### MORE YAML
in the YAML, this:    

```{{- if .Values.postgres.enabled }}```


if someone sets postgres.enabled: false (say, they're using an external managed Postgres instead of running one in-cluster), you don't want Helm to still create a postgres-secret that nothing uses. This guard makes the Secret's existence match the StatefulSet's existence — both created together, or neither created.