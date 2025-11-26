module.exports = {
  apps: [{
    name: 'chatbot-universitario',
    script: 'app.py',
    interpreter: 'python3',
    instances: 'max', // Usar todos los cores disponibles
    exec_mode: 'cluster', // Modo cluster para mejor rendimiento
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'development',
      FLASK_ENV: 'development',
      PORT: 5000
    },
    env_production: {
      NODE_ENV: 'production',
      FLASK_ENV: 'production',
      PORT: 5000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    // Configuración específica para Python/Flask
    interpreter_args: '-u',
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm Z',
    // Health check configuration
    health_check: {
      url: 'http://localhost:5000/health',
      interval: 30000, // 30 segundos
      timeout: 10000   // 10 segundos
    }
  }]
};