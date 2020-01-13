# Docker Image Version Watcher

## Description



## Limitations

- The only remote supported Docker registry is `index.docker.io` ;
- Does not work well with local image built `FROM` locally built image.

## Run command

```
docker pull theblusky/docker-image-version-watcher
docker run \
  --rm \
  -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  theblusky/docker-image-version-watcher
```

## Configuration

### Notification

| Environment variable | Description |
|----------------------|-------------|
| GOTIFY_URL           | Gotify notification URL (with API key)
| SLACK_URL            | Slack notification URL (with API key)
| SLACK_CHANNEL        | Slack notification channel (optional)
| SLACK_USERNAME       | Slack notification username (optional)
