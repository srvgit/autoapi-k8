kustomize build overlays/auto-api/dev > auto-api-graphlet_delete_me.yml

kubectl port-forward pod/generic-graphlet-55565d974b-dpx9r 9999:9090
