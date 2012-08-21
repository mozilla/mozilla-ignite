#!/bin/bash
python manage.py reset_db --router=default
python manage.py syncdb
python manage.py migrate
python manage.py challenges_dummy_content --development --submissions --winners --judging --webcast

