# ELK server configuration files

## Auth0 configuration
TODO: 

## Create .env file
Copy the `.env_template` file to create the `.env` file.

## Generate configs

By running
```bash
./generate_configs.sh
```

## Build ivs-monitor docker image
```bash
# These files have to be updated manually at the moment...
cd ~/broadcast-ivs-monitor-obs-media-monitoring/
sudo docker build -t obs-monitor-api ./obs-monitor-api/
```

## Start containers

```bash
sudo docker-compose up -d --build
```

## Stop containers

```bash
sudo docker-compose down
```

## Setup heartbeat

```bash
# This requires elastic user's password.
sudo ./heartbeat/setup.sh
```

## Reload Nginx configs
```bash
sudo docker exec elk_nginx_1 nginx -t
sudo docker exec elk_nginx_1 nginx -s reload
```
