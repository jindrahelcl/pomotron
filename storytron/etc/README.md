# StoryTRON Nginx Configuration

## Installation

1. Copy the nginx configuration:
   ```bash
   sudo cp etc/nginx-site.conf /etc/nginx/sites-available/pomotron
   ```

2. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/pomotron /etc/nginx/sites-enabled/
   ```

3. Test nginx configuration:
   ```bash
   sudo nginx -t
   ```

4. Reload nginx:
   ```bash
   sudo systemctl reload nginx
   ```

## Configuration Details

- **Location**: `/pomotron`
- **Backend**: Flask app running on `127.0.0.1:5000`
- **URL Rewriting**: Strips `/pomotron` prefix before forwarding to Flask
- **Headers**: Proper proxy headers for real IP and protocol detection

## Access URLs

With this configuration, StoryTRON will be accessible at:

- **Web Dashboard**: `http://your-server/pomotron/`
- **API Endpoints**: `http://your-server/pomotron/api/*`
- **Agent Management**: `http://your-server/pomotron/web/agents`
- **Chat Interface**: `http://your-server/pomotron/web/chat`

## Examples

```bash
# Keep-alive from PomoTRON
curl -X POST http://your-server/pomotron/api/keepalive

# List agents
curl http://your-server/pomotron/api/agents

# Switch agent
curl -X POST http://your-server/pomotron/api/agents/helper/activate

# Chat with agent
curl -X POST http://your-server/pomotron/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## Security (Optional)

Uncomment the auth_basic lines in the nginx config to add password protection:

```bash
# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd username
```

## Notes

- Flask app should still run on `127.0.0.1:5000` (localhost only)
- Nginx handles external access and proxies to Flask
- URL rewriting ensures Flask routes work correctly under `/pomotron`
