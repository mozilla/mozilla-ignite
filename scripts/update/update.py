"""
Deployment for mozillaignite

Requires commander (https://github.com/oremj/commander) which is installed on
the systems that need it.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commander.deploy import task, hostgroups

import commander_settings as settings

@task
def update_code(ctx, tag):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("git fetch origin")
        ctx.local("git checkout -f origin/%s" % tag)
        ctx.local("git submodule sync")
        ctx.local("git submodule update --init --recursive")
        ctx.local("find . -type f -name '.gitignore' -or -name '*.pyc' -delete")

@task
def checkin_changes(ctx):
    ctx.local(settings.DEPLOY_SCRIPT)


@hostgroups(settings.WEB_HOSTGROUP, remote_kwargs={'ssh_key': settings.SSH_KEY})
def deploy_app(ctx):
    ctx.remote(settings.REMOTE_UPDATE_SCRIPT)
    ctx.remote("/bin/touch %s" % settings.REMOTE_WSGI)


@task
def pre_update(ctx, ref=settings.UPDATE_REF):
    update_code(ref)


@task
def update(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("git rev-parse HEAD > media/revision")

@task
def deploy(ctx):
    pre_update()
    update()
    checkin_changes()
    deploy_app()
