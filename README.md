# prom-file-sd
Prometheus file service discovery with RESTful API

# Create directory for Prometheus data

```
mkdir -p prometheus_data
chown -R $USER:65534 prometheus_data
```

# Run

```
docker-compose up -d
```

# Add target

```
curl http://localhost:5000/targets -d '{
    "target": "localhost:9090",
	"env": "prom",
	"job": "prom"
}'
```

![Prometheus Targets](images/prom-targets.png)

# TODO
- [] Add Support custom `metrics_path`  (e.g. `/api/v1/metrics`)
- [] Add Web UI


### USE FILE-BASED SERVICE DISCOVERY TO DISCOVER SCRAPE TARGETS
https://prometheus.io/docs/guides/file-sd/