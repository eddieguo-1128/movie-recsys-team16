### On Server:

```bash
$ conda activate mlip
$ cd backend
```

**create .env:**

```
FLASK_ENV=dev  # dev/prod
HOST=127.0.0.1
PORT=8081   # If port taken by other members, just change one
```

**create .env.prod:**

```
FLASK_ENV=prod  # dev/prod
HOST=0.0.0.0
PORT=8082   # Never take port 8082 in development!
```

#### Run in Dev Mode:

```bash
$ python run.py # recommend!

or

$ docker compose up --build

```

#### Run in Prod Mode:

```bash
$ docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build   # recommend!

or

$ chmod +x run_prod.sh
$ ./run_prod.sh

```

### On your Computer:

```bash
$ ssh -L PORT:localhost:PORT your-user@your-remote-ip

```

- Or you can test it on server using `curl`


### Test Coverage
```bash
pytest --cov=app --cov-report=term-missing --cov-report=annotate tests/
```

### K8S Setup:

- minikube tunnel need to be ran in backend in a detached session:

```bash
# from user team16
minikube tunnel
```

```bash
docker build -f docker/Dockerfile.prod --build-arg VERSION=test3 -t zackyecmu/backend:test3 .

# Test image
docker run -p 8081:8081 zackyecmu/backend:test3

docker push zackyecmu/backend:test3

cd k8s
# Be sure to update the image tag in deployment.yaml first
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
# test on http://192.168.58.2:30080 on vm

kubectl get pods
kubectl get svc

# Delete
kubectl delete -f deployment.yaml
kubectl delete -f service.yaml
```

**Update Model**

```bash
kubectl set image deployment/backend-deployment backend=zackyecmu/backend:test3

kubectl rollout undo deployment/backend-deployment # Roll back to old image
```

### NGINX

```bash
sudo vim /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl reload nginx
```

```
http {
    # ... existing directives and includes ...

    server {
        listen 8082;
        server_name _;  # Matches any hostname

        location / {
            proxy_pass http://192.168.58.2:30080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```
