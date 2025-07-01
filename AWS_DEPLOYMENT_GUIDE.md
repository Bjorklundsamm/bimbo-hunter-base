# AWS EC2 Deployment Guide for Bimbo Hunter

## Prerequisites
- AWS Account with EC2 and Route 53 access
- Your "bimboxhunter.io" domain already purchased in Route 53
- SSH key pair for EC2 access

## Step 1: Launch EC2 Instance

1. **Go to EC2 Console** → Launch Instance
2. **Choose AMI**: Amazon Linux 2023 (latest)
3. **Instance Type**: t3.micro (sufficient for 8-10 players)
4. **Key Pair**: Select or create a new key pair
5. **Security Group**: Create new with these rules:
   - SSH (22): Your IP
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - Custom TCP (5000): 0.0.0.0/0 (temporary for testing)
6. **Storage**: 8 GB gp3 (default is fine)
7. **Launch Instance**

## Step 2: Connect to EC2 and Install Dependencies

```bash
# Connect to your instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y

# Install Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Install Python 3.11 and pip
sudo yum install -y python3.11 python3.11-pip

# Install Git
sudo yum install -y git

# Install Nginx
sudo yum install -y nginx

# Install PM2 for process management
sudo npm install -g pm2
```

## Step 3: Clone and Setup Your Application

```bash
# Clone your repository
git clone https://github.com/yourusername/bimbo-hunter-base.git
cd bimbo-hunter-base

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip3.11 install -r requirements.txt

# Install Node.js dependencies and build React app
cd client
npm install
npm run build
cd ..
```

## Step 4: Configure Application for Production

### 4.1: Create Production Configuration Override

```bash
# Make sure you're in the bimbo-hunter-base directory
cd /home/ec2-user/bimbo-hunter-base

# Create production config override file
cat > prod_config.py << 'EOF'
import os

# Override config for production
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5000
DEBUG_MODE = False

# Add your domain to CORS origins
CORS_ORIGINS = [
    'https://bimboxhunter.io',
    'https://www.bimboxhunter.io',
    'http://localhost:5000'
]

# Production database path (optional - keeps it in same location)
DB_FILE = "/home/ec2-user/bimbo-hunter-base/bhunter.db"

# Production logging
import logging
def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/home/ec2-user/bimbo-hunter-base/app.log', mode='a')
        ]
    )
EOF
```

### 4.2: Modify Your App to Use Production Config

```bash
# Create a simple script to patch your app.py for production
cat > apply_prod_config.py << 'EOF'
import sys
import os

# Add production config to the beginning of app.py
with open('app.py', 'r') as f:
    content = f.read()

# Check if already patched
if 'prod_config' not in content:
    # Add import for production config at the top
    lines = content.split('\n')

    # Find where to insert the production config import
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('from config import'):
            insert_index = i + 1
            break

    # Insert production config override
    prod_import = """
# Production configuration override
try:
    from prod_config import *
    print("✅ Production configuration loaded")
except ImportError:
    print("⚠️  Production config not found, using default config")
"""

    lines.insert(insert_index, prod_import)

    # Write back to file
    with open('app.py', 'w') as f:
        f.write('\n'.join(lines))

    print("✅ Production configuration applied to app.py")
else:
    print("✅ Production configuration already applied")
EOF

# Run the configuration script
python3.11 apply_prod_config.py
```

### 4.3: Set Environment Variables

```bash
# Create environment file for production
cat > .env.prod << 'EOF'
FLASK_ENV=production
PYTHONPATH=/home/ec2-user/bimbo-hunter-base
NODE_ENV=production
EOF

# Make the environment file readable
chmod 644 .env.prod
```

### 4.4: Update Start Script for Production Environment

```bash
# Create a wrapper script that loads environment variables
cat > start-prod-wrapper.sh << 'EOF'
#!/bin/bash
cd /home/ec2-user/bimbo-hunter-base

# Load production environment variables
if [ -f .env.prod ]; then
    export $(cat .env.prod | xargs)
fi

# Ensure virtual environment is activated
source venv/bin/activate

# Run the production start script
./start-app-prod.sh
EOF

# Make it executable
chmod +x start-prod-wrapper.sh
```

### 4.5: Verify Configuration

```bash
# Test that the configuration loads correctly
python3.11 -c "
try:
    from prod_config import *
    print('✅ Production config loaded successfully')
    print(f'Host: {DEFAULT_HOST}')
    print(f'Port: {DEFAULT_PORT}')
    print(f'Debug: {DEBUG_MODE}')
    print(f'CORS Origins: {CORS_ORIGINS}')
except Exception as e:
    print(f'❌ Error loading production config: {e}')
"
```

## Step 5: Create PM2 Ecosystem File

```bash
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'bimbo-hunter',
    script: './start-app-prod.sh',
    cwd: '/home/ec2-user/bimbo-hunter-base',
    interpreter: '/bin/bash',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/home/ec2-user/bimbo-hunter-base'
    },
    max_memory_restart: '500M',
    instances: 1,
    autorestart: true,
    watch: false,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
EOF
```

## Step 6: Configure Nginx as Reverse Proxy

```bash
sudo tee /etc/nginx/conf.d/bimboxhunter-io.conf << 'EOF'
server {
    listen 80;
    server_name bimboxhunter.io www.bimboxhunter.io;
    
    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;
    
    # Temporary direct proxy for initial setup
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Serve static files directly
    location /static/ {
        alias /home/ec2-user/bimbo-hunter-base/client/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Test nginx configuration
sudo nginx -t

# Start and enable nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Step 7: Setup Route 53 DNS

1. **Go to Route 53 Console** → Hosted Zones → bimboxhunter.io
2. **Create A Record**:
   - Name: (leave blank for root domain)
   - Type: A
   - Value: Your EC2 instance public IP
   - TTL: 300
3. **Create CNAME Record** (optional):
   - Name: www
   - Type: CNAME
   - Value: bimboxhunter.io
   - TTL: 300

## Step 8: Install SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo yum install -y python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d bimboxhunter.io -d www.bimboxhunter.io

# Test auto-renewal
sudo certbot renew --dry-run
```

## Step 9: Start Your Application

```bash
# Navigate to your app directory
cd /home/ec2-user/bimbo-hunter-base

# Start with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command it gives you (run with sudo)
```

## Step 10: Configure Auto-Deployment (Optional)

Create a simple deployment script:

```bash
cat > deploy.sh << 'EOF'
#!/bin/bash
cd /home/ec2-user/bimbo-hunter-base
git pull origin main
source venv/bin/activate
pip3.11 install -r requirements.txt
cd client && npm install && npm run build && cd ..
pm2 restart bimbo-hunter
EOF

chmod +x deploy.sh
```

## Step 11: Security Hardening

```bash
# Update security group to remove port 5000 access
# (only allow 80, 443, and SSH from your IP)

# Setup automatic security updates
sudo yum install -y yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

## Step 12: Monitoring and Logs

```bash
# View application logs
pm2 logs bimbo-hunter

# Monitor application
pm2 monit

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Final Verification

1. Visit `https://bimboxhunter.io` - should load your application
2. Test user registration and board generation
3. Verify all game functionality works
4. Check SSL certificate is valid

## Scaling Considerations

For future scaling with more players:
- Upgrade to t3.small or t3.medium
- Consider using RDS for database instead of SQLite
- Add CloudFront CDN for static assets
- Use Application Load Balancer for multiple instances

---

**Your application should now be live at `https://bimboxhunter.io`!**

The setup uses PM2 for process management, Nginx as a reverse proxy, and Let's Encrypt for SSL certificates, providing a robust and scalable foundation for your 8-10 player game.
