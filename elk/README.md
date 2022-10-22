# Auth0 configuration
TODO: 

# Create .env file
By copying the `.env_template` file

# Generate configs

By running
```
./generate_configs.sh
```

# Reload Nginx configs
```
sudo docker exec elk_nginx_1 nginx -t
sudo docker exec elk_nginx_1 nginx -s reload
```
