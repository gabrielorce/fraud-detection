
## Streamlit

The Streamlit App is executed with this command:   
```streamlit run your_script.py```   

This UI collects user input, calls the FastAPI ML service (<http://ml-service:8000/predict>), and displays the fraud risk probability.       



## CrashLoopBackOff   

During execution, i saw an error:   

```OSError: [Errno 24] inotify instance limit reached```

```inotify instance limit reached``` usually means the node/container has run out of Linux inotify resources. Streamlit watches files for changes, and its file-watcher can consume inotify instances/watches.

If you want you can confirm the relevant limits:    
```
cat /proc/sys/fs/inotify/max_user_instances
cat /proc/sys/fs/inotify/max_user_watches
```

One solution is to increase these limits.   

But - for a production Streamlit frontend, you often don't need aggressive file watching, since code doesn't change in PROD, this streamlit does not need to react to this. The execution was changed to:

You could start streamlit with:   
```streamlit run app.py --server.fileWatcherType none```   

Or configure it in ```.streamlit/config.toml```:
```
[server]
fileWatcherType = "none"
```    
Then rebuild/redeploy the frontend.


This is what I did in the dockerfile:  
```CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]```  

BUT I originally got an error.

```CMD ["streamlit", "run", "app.py", "--server.port 8501", " --server.address 0.0.0.0", "--server.fileWatcherType=none"]```  

Two things:  
1) The space right before  ``` --server.address``` caused an error.   
2) in CMD, we use the "=" sign instead of a space:   
``` --server.address=0.0.0.0```
