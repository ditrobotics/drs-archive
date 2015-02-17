from __future__ import print_function

from fabric.api import run, cd, local, env
from fabric.contrib.console import confirm
from fabric.colors import red
from fabric.network import needs_host
from fabric.utils import abort


jsontmppath = '/tmp/drs-dumped.json'
remote_media = '/home/afg/drs/media/drive/'


class CounterNullIO(object):
    def __init__(self, template='\r%d'):
        self.template = template
        self.count = 0

    def write(self, data):
        self.count += len(data)

    def flush(self):
        print(end=self.template % self.count)


def _confirm(destroy_target):
    print('The operation will', red('DESTROY', bold=True), 'all the data',
          'in', destroy_target, 'and sync from %r.' % env.host_string)
    if not confirm('Would you like to continue?', default=False):
        abort('Aborted.')


@needs_host
def syncdb(not_confirmed=True):
    if not_confirmed:
        _confirm('your local database')
    with cd('~/drs/'):
        jsons = run(
            'python3 manage.py dumpdata --natural-foreign --natural-primary',
            stdout=CounterNullIO('\rdumping data...(%d Bytes)')
        )
    print()
    with open(jsontmppath, mode='w') as file:
        file.write(jsons)
    local('python3 manage.py flush --noinput')
    local('python3 manage.py loaddata %s' % jsontmppath)


@needs_host
def syncmedia(not_confirmed=True):
    if not_confirmed:
        _confirm('your local media directory')
    local('mkdir -p media/drive/')
    local('rsync -ah --delete --info=progress2 %r:%r %r' % (
        env.host_string, remote_media, 'media/drive/'
    ))


def syncall():
    _confirm('your local database and media directory')
    syncdb(not_confirmed=False)
    syncmedia(not_confirmed=False)
