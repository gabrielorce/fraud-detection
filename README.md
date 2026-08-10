
# Fraud Detection Kubernetes-deployed Application

## Tech stack:
 
- Streamlit for frontend   




## Executing locally with Kind:

### 1. Create cluster
```kind create cluster --name fraud-cluster```  

#### 2. Build local images
```docker build -t local-registry/fraud-frontend:latest ./src/frontend```  
```docker build -t local-registry/fraud-ml-api:latest ./src/ml_service```  

#### 3. Load images into Kind cluster nodes  (exclusive to Kind)
```kind load docker-image local-registry/fraud-frontend:latest --name fraud-cluster```  
```kind load docker-image local-registry/fraud-ml-api:latest --name fraud-cluster```  

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


When all Pods show Running, port-forward to access the Streamlit UI in your browser:

```kubectl port-forward service/frontend-service 8501:80```   


Then open ```http://localhost:8501``` in your browser.



### More Helm commands


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

