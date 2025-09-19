#!/bin/bash

# PM2 Management Script for Memory Enterprise Frontend

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|monitor|dev|prod|build}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the application in development mode"
    echo "  stop    - Stop all PM2 processes"
    echo "  restart - Restart all PM2 processes"
    echo "  status  - Show PM2 process status"
    echo "  logs    - Show application logs"
    echo "  monitor - Open PM2 monitoring dashboard"
    echo "  dev     - Start in development mode with hot reload"
    echo "  prod    - Build and start in production mode"
    echo "  build   - Build the Next.js application"
    echo "  setup   - Setup PM2 startup script"
    echo "  save    - Save PM2 process list"
    echo "  flush   - Flush all logs"
}

case "$1" in
    start)
        echo -e "${GREEN}Starting Memory Enterprise Frontend (Development)...${NC}"
        pm2 start ecosystem.config.js --only memory-enterprise-dev
        pm2 status
        ;;

    stop)
        echo -e "${YELLOW}Stopping all PM2 processes...${NC}"
        pm2 stop all
        pm2 status
        ;;

    restart)
        echo -e "${YELLOW}Restarting PM2 processes...${NC}"
        pm2 restart all
        pm2 status
        ;;

    status)
        echo -e "${GREEN}PM2 Process Status:${NC}"
        pm2 status
        pm2 info memory-enterprise-dev 2>/dev/null || pm2 info memory-enterprise-frontend 2>/dev/null
        ;;

    logs)
        echo -e "${GREEN}Showing application logs...${NC}"
        pm2 logs --lines 50
        ;;

    monitor)
        echo -e "${GREEN}Opening PM2 monitoring dashboard...${NC}"
        pm2 monit
        ;;

    dev)
        echo -e "${GREEN}Starting in development mode...${NC}"
        pm2 delete memory-enterprise-dev 2>/dev/null
        pm2 start ecosystem.config.js --only memory-enterprise-dev
        pm2 logs memory-enterprise-dev
        ;;

    prod)
        echo -e "${GREEN}Building and starting in production mode...${NC}"
        echo "Building Next.js application..."
        npm run build

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Build successful! Starting production server...${NC}"
            pm2 delete memory-enterprise-frontend 2>/dev/null
            pm2 start ecosystem.config.js --only memory-enterprise-frontend --env production
            pm2 status
        else
            echo -e "${RED}Build failed! Please fix errors and try again.${NC}"
            exit 1
        fi
        ;;

    build)
        echo -e "${GREEN}Building Next.js application...${NC}"
        npm run build
        ;;

    setup)
        echo -e "${GREEN}Setting up PM2 startup script...${NC}"
        pm2 startup
        echo -e "${YELLOW}Follow the command above to setup auto-start on system boot${NC}"
        ;;

    save)
        echo -e "${GREEN}Saving PM2 process list...${NC}"
        pm2 save
        echo -e "${GREEN}Process list saved! Will auto-restore on PM2 restart.${NC}"
        ;;

    flush)
        echo -e "${YELLOW}Flushing all PM2 logs...${NC}"
        pm2 flush
        echo -e "${GREEN}Logs flushed successfully!${NC}"
        ;;

    *)
        print_usage
        exit 1
        ;;
esac