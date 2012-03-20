#!/bin/bash
python manage.py reset_db --router=default
python manage.py syncdb
python manage.py migrate
python manage.py loaddata fixtures/ignite.json
python manage.py bootstrap_test_fixtures