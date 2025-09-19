module.exports = {
  apps: [
    {
      name: 'memory-enterprise-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/home/jonghooy/work/rag-mcp/frontend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000/api/v1',
        BASE_PATH: '/kms',
        ASSET_PREFIX: '/kms'
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000/api/v1'
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'memory-enterprise-dev',
      script: 'npm',
      args: 'run dev',
      cwd: '/home/jonghooy/work/rag-mcp/frontend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: ['app', 'components', 'lib'],
      ignore_watch: ['node_modules', '.next', 'logs'],
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000/api/v1',
        BASE_PATH: '/kms',
        ASSET_PREFIX: '/kms'
      },
      error_file: './logs/pm2-dev-error.log',
      out_file: './logs/pm2-dev-out.log',
      log_file: './logs/pm2-dev-combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ],

  // Deploy configuration (optional)
  deploy: {
    production: {
      user: 'jonghooy',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'https://github.com/jonghooy/memory-enterprise-mcp.git',
      path: '/home/jonghooy/work/rag-mcp',
      'post-deploy': 'cd frontend && npm install && npm run build && pm2 reload ecosystem.config.js --env production',
      'pre-deploy-local': ''
    }
  }
};