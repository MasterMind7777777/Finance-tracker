import os

# Define apps and their log files
APP_LOG_FILES = {
    "django": "django.log",
    "analytics": "analytics.log",
    "api_v1": "api_v1.log",
    "budgets": "budgets.log",
    "capital": "capital.log",
    "core": "core.log",
    "finance_tracker": "finance_tracker.log",
    "transactions": "transactions.log",
    "users": "users.log",
    "react_loging_views" : "react_loging_views.log"
}

CELERY_APP_LOG_FILES = {
    "analytics_celery": "analytics_celery.log",
    "budgets_celery": "budgets_celery.log",
    "capital_celery": "capital_celery.log",
    "core_celery": "core_celery.log",
    "transactions_celery": "transactions_celery.log",
    "users_celery": "users_celery.log",
}

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Ensure logs directory exists
if not os.path.exists("logs/celery"):
    os.makedirs("logs/celery")

# Generate handlers based on app log files
handlers = {
    app_name: {
        "level": "DEBUG",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join("logs", log_file)
        if app_name != "celery"
        else os.path.join("logs/celery", log_file),
        "maxBytes": 10 * 1024 * 1024,  # Rotate after 10 MB
        "backupCount": 5,  # Keep 5 backup copies
        "formatter": "json",
    }
    for app_name, log_file in {**APP_LOG_FILES, **CELERY_APP_LOG_FILES}.items()
}

# Generate loggers based on apps
loggers = {
    app_name: {
        "handlers": [app_name],  # the handler's key is the app's name itself
        "level": "DEBUG",
        "propagate": app_name
        == "django",  # propagate only for 'django' as in the initial config
    }
    for app_name in {**APP_LOG_FILES, **CELERY_APP_LOG_FILES}.keys()
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(levelname)s %(asctime)s %(module)s %(message)s",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": handlers,
    "loggers": loggers,
}
