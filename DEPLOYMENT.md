# Memory Enterprise KMS Deployment Guide

## 🎉 Successfully Deployed!

The Memory Enterprise Knowledge Management System is now deployed and accessible at:

### 🌐 Access URLs

- **Production URL**: https://www.llmdash.com/kms/
- **Alternative URLs**:
  - https://llmdash.com/kms/
  - https://124.194.32.36/kms/

## 📋 Deployment Configuration

### Nginx Setup
The application is served through Nginx with the following configuration:
- **Upstream**: `localhost:3000` → KMS frontend
- **Base Path**: `/kms/`
- **SSL**: Enabled with Let's Encrypt certificates

### PM2 Process Management
The application is managed by PM2:
- **Process Name**: `memory-enterprise-frontend`
- **Mode**: Production
- **Port**: 3000
- **Auto-restart**: Enabled
- **Logs**: `/home/jonghooy/work/rag-mcp/frontend/logs/`

### Next.js Configuration
- **Base Path**: `/kms`
- **Asset Prefix**: `/kms`
- **Trailing Slash**: Enabled for Nginx compatibility

## 🚀 Management Commands

### PM2 Commands
```bash
# Check status
pm2 status

# View logs
pm2 logs memory-enterprise-frontend

# Restart application
pm2 restart memory-enterprise-frontend

# Stop application
pm2 stop memory-enterprise-frontend

# Monitor resources
pm2 monit
```

### Development Commands
```bash
# Navigate to frontend directory
cd /home/jonghooy/work/rag-mcp/frontend

# Build for production
npm run build

# Start development server
npm run pm2:dev

# Start production server
npm run pm2:prod
```

### Nginx Commands
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

## 📁 Project Structure

```
/home/jonghooy/work/rag-mcp/
├── frontend/                    # Next.js application
│   ├── app/                    # App router pages
│   ├── components/             # React components
│   ├── lib/                    # Utilities and configs
│   ├── ecosystem.config.js     # PM2 configuration
│   ├── .env.production        # Production environment variables
│   └── logs/                  # PM2 log files
├── nginx-kms.conf             # Nginx configuration reference
├── PM2_MANAGEMENT.md          # PM2 management guide
└── DEPLOYMENT.md              # This file
```

## 🔧 Configuration Files

### Nginx Configuration
Location: `/etc/nginx/sites-available/llmdash`
```nginx
upstream kms_frontend {
    server localhost:3000;
}

location /kms/ {
    proxy_pass http://kms_frontend/;
    # ... proxy settings
}
```

### PM2 Configuration
Location: `/home/jonghooy/work/rag-mcp/frontend/ecosystem.config.js`
```javascript
{
  name: 'memory-enterprise-frontend',
  script: 'npm',
  args: 'start',
  env: {
    NODE_ENV: 'production',
    PORT: 3000,
    BASE_PATH: '/kms',
    ASSET_PREFIX: '/kms'
  }
}
```

### Environment Variables
Location: `/home/jonghooy/work/rag-mcp/frontend/.env.production`
```env
BASE_PATH=/kms
ASSET_PREFIX=/kms
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 📊 Current Status

✅ **Nginx**: Configured and running
✅ **PM2**: Process active and monitored
✅ **Next.js**: Built and serving pages
✅ **HTTPS**: SSL certificates active
✅ **Routing**: Base path `/kms` configured

## 🔍 Troubleshooting

### Application Not Loading
1. Check PM2 status: `pm2 status`
2. Check logs: `pm2 logs memory-enterprise-frontend`
3. Verify port 3000: `lsof -i :3000`

### 404 Errors
1. Ensure build includes base path: `BASE_PATH=/kms npm run build`
2. Check Nginx configuration: `sudo nginx -t`
3. Verify routes in Next.js app

### SSL Issues
1. Check certificate status: `sudo certbot certificates`
2. Verify Nginx SSL configuration
3. Test with curl: `curl -I https://www.llmdash.com/kms/`

## 🎯 Next Steps

1. **Connect Backend**:
   - Deploy FastAPI backend at port 8000
   - Update API_URL in environment variables

2. **Enable Features**:
   - Connect to vector database (Pinecone/Qdrant)
   - Set up Google Docs integration
   - Configure MCP server

3. **Monitoring**:
   - Set up PM2 Plus for advanced monitoring
   - Configure log rotation
   - Add health checks

## 📝 Notes

- The application is currently serving static pages
- Backend integration pending (FastAPI at port 8000)
- Database connections need to be configured
- Authentication system to be implemented later