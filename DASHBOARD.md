
# Kubernetes Dashboard  


The Kubernetes Dashboard project has been archived and is no longer actively maintained. For new installations, consider using Headlamp.  

<https://headlamp.dev/>  


In-cluster installation:  
<https://headlamp.dev/docs/latest/installation/in-cluster/>


```
# First add our custom repo to your local helm repositories.
# then you should be able to install headlamp via helm.

helm repo add headlamp https://kubernetes-sigs.github.io/headlamp/
helm install my-headlamp headlamp/headlamp --namespace kube-system
```