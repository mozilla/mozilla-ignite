===============
Mozilla Ignite
===============

mozilla-ignite is a challenge and participation platform that's being built on-top of the [betafarm architecture]: https://github.com/mozilla/betafarm

The Project structure is based on Mozilla Playdoh http://playdoh.readthedocs.org/en/latest/index.html


Contributing
------------

Patches are welcome! Feel free to fork and contribute to this project on
[github][gh-betafarm].

[gh-betafarm]: https://github.com/rossbruniges/mozilla-ignite


Installation
============

The recommended setup is using [vagrant](http://vagrantup.com/) and [virtual box](https://www.virtualbox.org/wiki/Downloads)


Getting the source code
-----------------------

Clone the repository and its dependencies:

    git clone --recursive git@github.com:rossbruniges/mozilla-ignite.git

This will take a few minutes.

This will keep the code living in your filesystem but the application running inside a VM.

Once you've installed vagrant, from the root of the repository copy the local vagrant settings.

    cp vagrantconfig_local.yaml-dist vagrantconfig_local.yaml

Edit ``vagrantconfig_local.yaml`` if you want to change any of the defaults.

If you are on an NFS capable OS I recommend that you change ``nfs`` to ``true``.

VirtualBox has know issues sharing files natively, more about this: http://vagrantup.com/docs/nfs.html


Update the local settings file
==============================

From the root of the repository copy the local python settings.

    cp settings_local.py-dist settings_local.py

Amend ``popcorn_gallery/settings/local.py``  adding your details:

- ADMINS: Add an email address and a name.
- SECRET_KEY: This can be anything.
- HMAC_KEYS: Uncomment or add your own key inside it.


Start the VM
============

Now we are ready to provision the machine run.

    vagrant up

This will take a few minutes, so go on and reward yourself with a nice cup of tea!



Add a host alias
================

This is done so you can access the application via: http://local.mozillaignite.org and perform the browserid assertion.

If you are on OSX or *NIX add an alias for the site by running the following command in your local machine:

    echo "33.33.33.12 local.mozillaignite.org" | sudo tee -a /etc/hosts

Or if you prefer a GUI try http://code.google.com/p/gmask/

Now the application should be available at:

    http://local.mozillaignite.org


Creating a superuser
====================

From inside the VM run:

    python manage.py createsuperuser


Setup the application
---------------------

You've need git and pip installed on the machine you want to install it on

1. Clone the repo
2. Install the dependancies:
    * pip install -r requirements/dev.txt
    * pip install -r requirements/compiled.txt
    * git submodule update --init --recursive
3. Create local settings file
    * cp settings_local.py-dist settings_local.py
4. Create local database
5. Insert name and login details in settings_local.py
6. Uncomment and specify an HMAC_KEYS entry
7. Create generic database tables:
    * ./manage.py syncdb
8. Create mozilla-ignite specific database tables:
    * ./manage.py migrate
9. Compress your assets
    * ./manage.py compress_assets



License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/

