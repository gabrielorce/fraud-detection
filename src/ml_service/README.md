# Comments on the ML-related side 


## ML Model path and helm chart:

MODEL_PATH is being defined by Kubernetes through the Helm deployment

```MODEL_PATH=/mnt/data/fraud_model.pkl```   

But Kubernetes is mounting a volume into the container at:

```/mnt/data```   

So the overall set up is:   

```
Kubernetes Pod      
│     
├── Container: ml-api      
│   │     
│   ├── Environment variable:   
│   │     MODEL_PATH=/mnt/data/fraud_model.pkl   
│   │   
│   └── /mnt/data  ◄──── mounted volume   
│          │   
│          └── fraud_model.pkl   
│    
└── Volume: ml-data-volume   
```

Therefore the app looks for the model in ```/mnt/data/fraud_model.pkl``` inside the container, but that ```/mnt/data directory``` is actually backed by the external Kubernetes volume at node level.


## FASTAPI's app decorator:

```
app = FastAPI()
...
@app.on_event("startup")
```


It is a FASTAPI decorator:    
<https://fastapi.tiangolo.com/advanced/events/>



ALSO:
In docker we have:

```CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]```   


This is referring to the main.py file, where "app" is defined in:   

```app = FastAPI()```   


## UVICORN:    
<https://uvicorn.dev/#quickstart>    
<https://medium.com/@iklobato/mastering-gunicorn-and-uvicorn-the-right-way-to-deploy-fastapi-applications-aaa06849841e>   
<https://oneuptime.com/blog/post/2026-02-03-python-uvicorn-production/view>   



