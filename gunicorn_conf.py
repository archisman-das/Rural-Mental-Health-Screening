import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 1
threads = 4
timeout = 120
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
capture_output = True
