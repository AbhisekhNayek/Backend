import multiprocessing
import os

# Gunicorn configuration
bind = "0.0.0.0:" + os.getenv("PORT", "8000")

# Worker configuration
# Standard recommendation: (2 x num_cores) + 1
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts and limits
timeout = int(os.getenv("TIMEOUT", "120"))
keepalive = int(os.getenv("KEEP_ALIVE", "5"))

# Logging
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"

# Forwarded headers (important for reverse proxies like Nginx/Load Balancers)
forwarded_allow_ips = "*"
