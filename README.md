===============
Mozilla Ignite
===============

``mozilla-ignite`` is a challenge and participation platform that's being built on-top of the [betafarm architecture]: https://github.com/mozilla/betafarm

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

Amend ``settings_local.py``  adding your details:

- ADMINS: Add an email address and a name.
- SECRET_KEY: Used to provide a seed in secret-key hashing algorithms. Set this to a random string -- the longer, the better
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


Updating the application
========================

The application is under develpment and from time to time there could be database changes.

There is an script is provided to make sure it is keep in sync

SSH into the VM:

    vagrant ssh

Run the update script

    fab update_local


Updating the VM
===============

The virtual machine can be updated from time to time, and it is done via Puppet http://puppetlabs.com/

Update the server by running in your local machine from the root of the project:

    vagrant provision


Runing the test suite
=====================

SSH into the virtualbox:

    vagrant ssh

And run the test suite:

    fab test

Compress the assets
===================

SSH into the virtual box:

    vagrant ssh

Stop apache:

    sudo /etc/init.d/apache2 stop

Run the development server

    python manage.py compress_assets


Creating a superuser
====================

From inside the VM run:

    python manage.py createsuperuser


Speed up the server
===================

At the moment the wsgi application is served via apache, which it's a bit hacky in order to pick up the file changes and reload automaticaly.

If you want to speed up the application you could try stop apache and run the application via the development server.

NGINX is proxy-passing the port 8000 to 80 and serving most of the static and media  files.

SSH into the virtual box:

    vagrant ssh

Stop apache:

    sudo /etc/init.d/apache2 stop

Run the development server

    python manage.py runserver


License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/

