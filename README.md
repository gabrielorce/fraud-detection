
# Fraud Detection Kubernetes-deployed Application

## Architecture:


                                    [ User Browser ]  
                                            │  
                                            ▼ (HTTP :80 / :8501)  
                                 ┌──────────────────────┐    
                                 │   Frontend (Pod)     │    
                                 │  (Streamlit / Python)│    
                                 └──────────┬───────────┘     
                                            │    
                 ┌──────────────────────────┴──────────────────────────┐   
                 │ Internal HTTP                                       │ Internal DB Query   
                 ▼ (:8000)                                             ▼ (:5432)   
    ┌─────────────────────────┐                               ┌─────────────────┐   
    │ Fraud ML API (Pod)      │                               │ PostgreSQL (Pod)│   
    │ (FastAPI + Scikit-Learn)│                               │ (StatefulSet)   │   
    └────────────┬────────────┘                               └────────┬────────┘   
                 │ Reads Model / Training Data                         │   
                 ▼                                                     ▼   
    ┌─────────────────────────┐                               ┌─────────────────┐   
    │ PersistentVolumeClaim   │                               │ PostgreSQL PVC  │   
    │ (/data/fraud_model.pkl) │                               │ (/var/lib/data) │   
    └─────────────────────────┘                               └─────────────────┘   


## Tech stack:
 
- Streamlit for frontend   
- PostgreSQL as database


## File Structure:
    fraud-detection-chart/      
    ├── Chart.yaml      
    ├── values.yaml 
    └── templates/  
        ├── postgres-statefulset.yaml   
        ├── postgres-service.yaml   
        ├── ml-deployment.yaml  
        ├── ml-service.yaml 
        ├── ml-pvc.yaml                <-- Mounts external training data / model    
        ├── frontend-deployment.yaml    
        └── frontend-service.yaml   


    fraud-detection/
        ├── helm/
        │   └── fraud-detection-chart/
        │       ├── Chart.yaml
        │       ├── values.yaml
        │       ├── scripts/
        │       │   └── train_model.py         <-- Place training script here
        │       └── templates/
        │           ├── ml-configmap.yaml      <-- Uses .Files.Get "scripts/train_model.py"
        │           ├── ml-deployment.yaml
        │           ├── frontend-deployment.yaml
        │           └── postgres-statefulset.yaml
        ├── src/
        │   ├── frontend/
        │   │   ├── Dockerfile
        │   │   ├── app.py
        │   │   └── requirements.txt
        │   └── ml_service/
        │       ├── Dockerfile
        │       ├── main.py
        │       └── requirements.txt
        ├── .gitignore
        └── .dockerignore



## Executing locally with Kind:

### 1. Create cluster
```kind create cluster --name fraud-cluster```  

#### 2. Build local images
```docker build -t local-registry/fraud-frontend:latest ./src/frontend```  
```docker build -t local-registry/fraud-ml-api:latest ./src/ml_service```  

#### 3. Load images into Kind cluster nodes  (exclusive to Kind)
```kind load docker-image local-registry/fraud-frontend:latest --name fraud-cluster```  
```kind load docker-image local-registry/fraud-ml-api:latest --name fraud-cluster```    
 
NOTE: ```local-registry``` is just a placeholder for a Container Registry domain or namespace. It can actually have any name (e.g., ```my-registry```).   


#### 4. Deploy the Helm Chart

Syntax:    
```helm install <release-name> <path-to-chart>```   
Here:   
```helm install fraud-app ./helm/fraud-detection-chart```    

If you already installed it previously, run this instead:   
```helm upgrade fraud-app ./helm/fraud-detection-chart```   

You can also upgrade (after you change the chart or values):  
```helm upgrade fraud-app ./helm/fraud-detection-chart```    


See more commands below.  

#### 5. Check Pod status
```kubectl get pods -w```      

The -w (or --watch) flag tells kubectl to stream real-time updates rather than returning to the command prompt.   


#### 6. When all Pods show Running, port-forward to access the Streamlit UI in your browser:

```kubectl port-forward service/frontend-service 8501:80```   


Then open ```http://localhost:8501``` in your browser.

if port is already in use, you can kill the corresponding process using it:    
```sudo fuser -k 8501/tcp```     


### More Helm commands


#### Validate chart syntax
```helm lint fraud-detection-chart/```

#### Dry run local render
```helm install fraud-demo fraud-detection-chart/ --dry-run```



Install or upgrade in one command (handy for CI/CD or repeated runs)  
```helm upgrade --install fraud-app ./helm/fraud-detection-chart```

Override values without editing values.yaml:  
```helm install fraud-app ./helm/fraud-detection-chart --set replicaCount=3 --set image.tag=v2.0.1```

Or point to a different values file:  
```helm install fraud-app ./helm/fraud-detection-chart -f values-prod.yaml```    

Preview what will be applied (without actually deploying):  
```helm template fraud-app ./helm/fraud-detection-chart```    
or   
```helm install fraud-app ./helm/fraud-detection-chart  --dry-run --debug```    

Check status / list releases:  
```
helm list
helm status myapp
```

Rollback if something breaks:   
```helm install fraud-app <revision-number>```   

Uninstall:   
```helm uninstall fraud-app```



Typical workflow once your chart is ready:

1) ```helm template myapp ./mychart``` — sanity check the output   
2) ```helm install myapp ./mychart --namespace mynamespace --create-namespace``` — first deploy   
3) Make changes → ```helm upgrade myapp ./mychart``` — subsequent deploys   

One thing worth checking before you run install: make sure your ```kubectl``` context is pointed at the right cluster (```kubectl config current-context```), since Helm just uses whatever context kubectl is configured with.




Troubleshooting:   
Check if ML model is being loaded.   
1) Check the ```/health``` Endpoint

```
# Forward ML service port if not already forwarded
kubectl port-forward service/ml-service 8000:8000
```

then check via web browser or via curl:   
```curl http://localhost:8000/health```
   
   
   
To restart the ML service deployment after a change:   
```kubectl rollout restart deployment/ml-fraud-service```   







# Restarting the Kubernetes Setup  

## Soft-restart:  

If you made code changes, updated Docker images, or just want all pods to restart without destroying your PostgreSQL database, perform a rolling restart:  
```
# Force Kubernetes to restart all deployments and statefulsets
kubectl rollout restart deployment/frontend-ui
kubectl rollout restart deployment/ml-fraud-service
kubectl rollout restart statefulset/postgres-0
```

To watch them terminate and boot back up:   
kubectl get pods -w

## Helm Uninstall & Reinstall (Clean State):   
If you modified your Helm templates or values and want to wipe out the current release (including ephemeral storage) and redeploy fresh:   

```
# 1. Uninstall the Helm release
helm uninstall fraud-app

# 2. Delete any lingering PVCs if you want a totally fresh database (Optional)
kubectl delete pvc --all

# 3. Re-install the chart
helm install fraud-app ./helm/fraud-detection-chart
```


## Full Cluster Nuke & Rebuild (Nuclear Option)

If your local cluster state gets corrupted, or images are cached awkwardly in memory: 
FOR KIND:
```
# 1. Destroy cluster
kind delete cluster --name fraud-cluster

# 2. Recreate cluster
kind create cluster --name fraud-cluster

# 3. Load host Docker images into cluster
kind load docker-image local-registry/fraud-frontend:latest --name fraud-cluster
kind load docker-image local-registry/fraud-ml-api:latest --name fraud-cluster

# 4. Deploy fresh
helm install fraud-app ./helm/fraud-detection-chart
```   


If you were using port forwarding to access the Streamlit UI or FastAPI metrics, restart your port forward command in a dedicated terminal window:    

```kubectl port-forward service/frontend-service 8501:80```    
    
to kill the process using this port:
sudo fuser -k 8501/tcp

