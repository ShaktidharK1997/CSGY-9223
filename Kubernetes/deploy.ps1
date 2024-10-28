# deploy.ps1
Write-Host "Deploying MongoDB..."
kubectl apply -f mongodb.yaml

Write-Host "Waiting for MongoDB deployment..."
Start-Sleep -Seconds 10

Write-Host "Deploying Flask application..."
kubectl apply -f flask-app.yaml

Write-Host "Waiting for Flask deployment..."
Start-Sleep -Seconds 10

Write-Host "Getting service URL..."
minikube service todo-flask-service --url

Write-Host "Deployment complete! Use the URL above to access your application."