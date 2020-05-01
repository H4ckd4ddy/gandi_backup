# gandi_backup

Use Gandi API v5 to backup all your all your DNS records & email forwarding, in case of misconfiguration or major outage.

When you count more than a hundred records and redirects, you don't want to lose them ...


##### With docker (for one shot backup) :
```
docker run \
--env API_KEY=your_gandi_api_key \
--env INTERVAL=0 \
-v gandi_backup_data:/data \
-d hackdaddy/gandi_backup
```

##### With docker-compose (backup every 24h) :
```
version: '3.7'
services:
  gandi_backup:
    image: hackdaddy/gandi_backup
    container_name: Gandi_backup
    environment:
      API_KEY: your_gandi_api_key
      INTERVAL: 24
    volumes:
    	- type: bind
    	  source: /your/backup/folder
    	  targer: /data
    restart: always
```