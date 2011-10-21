mozilla-ignite
==============

mozilla-ignite is a challenge and participation platform that's being built on-top of the [betafarm architecture]: https://github.com/mozilla/betafarm 

Contributing
------------

Patches are welcome! Feel free to fork and contribute to this project on
[github][gh-betafarm].

[gh-betafarm]: https://github.com/rossbruniges/mozilla-ignite

Installation
------------

You've need git and pip installed on the machine you want to install it on

1. Clone the repo
        git clone git@github.com:rossbruniges/mozilla-ignite.git
2. Install the dependancies:
        pip install -r requirements/dev.txt
        pip install -r requirements/compiled.txt
        git submodule init
        git submodule update
        cd vendor/
        git submodule init
        git submodule update
3. Create local settings file
        cp settings_local.py-dist settings_local.py
4. Create local database
5. Insert name and login details in settings_local.py
6. Uncomment and specify an HMAC_KEYS entry
7. Create generic database tables:
        ./manage.py syncdb
8. Create mozilla-ignite specific database tables:
        ./manage.py migrate

License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/

