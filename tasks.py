"""Tasks for invoke."""

from invoke import task, run


@task
def test():
    run('./setup.py test --quick')


@task
def fulltest():
    run('./setup.py test')


@task
def coverage():
    run('./setup.py test', hide='stdout')
    run('coverage html')
