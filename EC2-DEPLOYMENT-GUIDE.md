# EC2 Deployment Guide for Bimbo Hunter

## Prerequisites
- Fresh Linux EC2 instance (Amazon Linux 2023 or Ubuntu)
- Domain `bimbo.zone` configured in Route 53
- AWS Console access or SSH access to your EC2 instance
- Git repository with latest commits pushed

## Step 1: Initial EC2 Setup

### 1.1 Connect to your EC2 instance
**Option A: AWS Console (what you're using)**
- Use EC2 Instance Connect in AWS Console

**Option B: SSH**
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip  # Amazon Linux
# OR
ssh -i your-key.pem ubuntu@your-ec2-ip    # Ubuntu
```

### 1.2 Update the system
**For Amazon Linux 2023:**
```bash
sudo dnf update -y
```

**For Amazon Linux 2:**
```bash
sudo yum update -y
```

**For Ubuntu:**
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Install required packages

**For Amazon Linux 2023:**
```bash
# Install Python 3.11, pip, git, nginx
sudo dnf install -y python3.11 python3.11-pip git nginx

# Install Node.js 18.x (LTS)
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs

# Verify installations
python3.11 --version
node --version
npm --version
nginx -v
```

**For Amazon Linux 2:**
```bash
# Install Python 3, pip, git, nginx
sudo yum install -y python3 python3-pip git nginx

# Install Node.js 18.x (LTS)
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Verify installations
python3 --version
node --version
npm --version
nginx -v
```

**For Ubuntu:**
```bash
# Install Python 3.11, pip, git, nginx, and Node.js
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx curl

# Install Node.js 18.x (LTS)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3.11 --version
node --version
npm --version
nginx -v
```

## Step 2: Clone and Setup Project

### 2.1 Clone your repository
**For Amazon Linux (ec2-user):**
```bash
cd /home/ec2-user
git clone https://github.com/your-username/bimbo-hunter-base.git
cd bimbo-hunter-base
```

**For Ubuntu:**
```bash
cd /home/ubuntu
git clone https://github.com/your-username/bimbo-hunter-base.git
cd bimbo-hunter-base
```

### 2.2 Create Python virtual environment
**For Amazon Linux 2023:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

**For Amazon Linux 2:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**For Ubuntu:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 2.3 Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Install Node.js dependencies
```bash
# Install root dependencies
npm install

# Install client dependencies
cd client
npm install
cd ..
```

## Step 3: Build the Application

### 3.1 Create production build
```bash
cd client
npm run build
cd ..
```

### 3.2 Initialize database
```bash
source venv/bin/activate
python3 -c "from database import init_db; init_db()"
```

### 3.3 Test the application locally
```bash
# Make start script executable
chmod +x start-app-prod.sh

# Test run (Ctrl+C to stop)
./start-app-prod.sh
```

## Step 4: Configure Nginx

### 4.1 Create Nginx configuration

**For Amazon Linux (using conf.d directory):**
```bash
sudo nano /etc/nginx/conf.d/bimbo-hunter.conf
```

**For Ubuntu (using sites-available):**
```bash
sudo nano /etc/nginx/sites-available/bimbo-hunter
```

Add this configuration to the file:
```nginx
server {
    listen 80;
    server_name bimbo.zone www.bimbo.zone;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy to Flask application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Handle large file uploads
    client_max_body_size 16M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

### 4.2 Enable the site

**For Amazon Linux:**
```bash
# Remove default configuration if it exists
sudo rm -f /etc/nginx/conf.d/default.conf
# Test configuration
sudo nginx -t
# Restart nginx
sudo systemctl restart nginx
```

**For Ubuntu:**
```bash
sudo ln -s /etc/nginx/sites-available/bimbo-hunter /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## Step 5: Configure Domain (Route 53)

### 5.1 Point domain to EC2
In AWS Route 53:
1. Go to your hosted zone for `bimbo.zone`
2. Create/update A record:
   - Name: `@` (root domain)
   - Type: `A`
   - Value: `your-ec2-public-ip`
   - TTL: `300`
3. Create CNAME record for www:
   - Name: `www`
   - Type: `CNAME`
   - Value: `bimbo.zone`
   - TTL: `300`

## Step 6: Setup SSL with Let's Encrypt

### 6.1 Install Certbot
**For Amazon Linux:**
```bash
sudo dnf install -y certbot python3-certbot-nginx
# OR for Amazon Linux 2:
# sudo yum install -y certbot python3-certbot-nginx
```

**For Ubuntu:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 6.2 Obtain SSL certificate
```bash
sudo certbot --nginx -d bimbo.zone -d www.bimbo.zone
```

Follow the prompts and select option 2 (redirect HTTP to HTTPS).

## Step 7: Create Systemd Service

### 7.1 Create service file
```bash
sudo nano /etc/systemd/system/bimbo-hunter.service
```

Add this content:
```ini
[Unit]
Description=Bimbo Hunter Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/bimbo-hunter-base
Environment=PATH=/home/ec2-user/bimbo-hunter-base/venv/bin
ExecStart=/home/ec2-user/bimbo-hunter-base/venv/bin/python app.py

# NOTE: For Ubuntu, change ec2-user to ubuntu in the above lines
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7.2 Enable and start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable bimbo-hunter
sudo systemctl start bimbo-hunter
sudo systemctl status bimbo-hunter
```

## Step 8: Configure Firewall

### 8.1 Setup Firewall
**For Amazon Linux (using firewalld):**
```bash
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

**For Ubuntu (using UFW):**
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

## Step 9: Final Testing

### 9.1 Test the application
1. Visit `https://bimbo.zone` in your browser
2. Check that all features work correctly
3. Test file uploads
4. Verify database functionality

### 9.2 Monitor logs
```bash
# Application logs
sudo journalctl -u bimbo-hunter -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Step 10: Maintenance Commands

### 10.1 Update application
**For Amazon Linux:**
```bash
cd /home/ec2-user/bimbo-hunter-base
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd client && npm install && npm run build && cd ..
sudo systemctl restart bimbo-hunter
```

**For Ubuntu:**
```bash
cd /home/ubuntu/bimbo-hunter-base
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd client && npm install && npm run build && cd ..
sudo systemctl restart bimbo-hunter
```

### 10.2 View application status
```bash
sudo systemctl status bimbo-hunter
sudo systemctl status nginx
```

### 10.3 Restart services
```bash
sudo systemctl restart bimbo-hunter
sudo systemctl restart nginx
```

## Troubleshooting

### Common Issues:
1. **Port 5000 already in use**: Check with `sudo lsof -i :5000` and kill process
2. **Permission denied**: Ensure correct user owns project files:
   - Amazon Linux: `sudo chown -R ec2-user:ec2-user /home/ec2-user/bimbo-hunter-base`
   - Ubuntu: `sudo chown -R ubuntu:ubuntu /home/ubuntu/bimbo-hunter-base`
3. **Build fails**: Check Node.js version and clear cache: `cd client && npm cache clean --force && npm install`
4. **Database issues**: Recreate database: `rm bhunter.db && python3 -c "from database import init_db; init_db()"`

### Log Locations:
- Application: `sudo journalctl -u bimbo-hunter`
- Nginx: `/var/log/nginx/`
- Application file: `/home/ec2-user/bimbo-hunter-base/app.log` (or `/home/ubuntu/bimbo-hunter-base/app.log` for Ubuntu)

## Security Notes
- Keep system updated: `sudo apt update && sudo apt upgrade`
- Monitor logs regularly
- Consider setting up automated backups for the database
- Review firewall rules periodically

Your application should now be live at https://bimbo.zone! 🎉
