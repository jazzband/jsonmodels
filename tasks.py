"""Tasks for invoke."""

from invoke import task, run


@task
def test():
    """Run quick tests."""
    run('./setup.py test --quick')


@task
def fulltest():
    """Run full tests."""
    run('./setup.py test')
