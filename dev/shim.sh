#!/bin/bash

export OTEL_METRICS_EXPORTER=none
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT="api.honeycomb.io:443"
export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=cZX0pecOaRY6AnM4LoPECF"
export OTEL_SERVICE_NAME="dev-django-ddb-sessions"
export DJANGO_SETTINGS_MODULE="dev.settings"
export OTEL_LOG_LEVEL="debug"

opentelemetry-instrument python manage.py runserver --noreload
