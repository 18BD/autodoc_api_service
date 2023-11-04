#!/bin/bash
set -e

sleep 10

exec celery -A app worker -l info