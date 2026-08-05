
Executing locally with Kind:

### 1. Create cluster
```kind create cluster --name fraud-cluster```  

#### 2. Build local images
```docker build -t local-registry/fraud-frontend:latest ./src/frontend```  
```docker build -t local-registry/fraud-ml-api:latest ./src/ml_service```  

#### 3. Load images into Kind cluster nodes  (exclusive to Kind)
```kind load docker-image local-registry/fraud-frontend:latest --name fraud-cluster```  
```kind load docker-image local-registry/fraud-ml-api:latest --name fraud-cluster```  

#### 4. Deploy the Helm Chart
```helm install fraud-app ./helm/fraud-detection-chart```   

#### 5. Check Pod status
```kubectl get pods -w```     


To view the Streamlit UI in your browser with Kind:     

```kubectl port-forward service/frontend-service 8501:80```   


Then open ```http://localhost:8501``` in your browser.