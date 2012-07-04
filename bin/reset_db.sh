#!/bin/bash
python manage.py reset_db --router=default
python manage.py syncdb
python manage.py migrate

