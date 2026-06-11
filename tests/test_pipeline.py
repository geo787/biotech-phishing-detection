import pytest
from run_demo import run_demo


def test_run_demo_returns_list():
    results = run_demo()
    assert isinstance(results, list)
    assert len(results) >= 1


if __name__ == '__main__':
    run_demo()
