import os
import sys

# Ensure src module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_project_structure():
    """Checks if key directories exist."""
    assert os.path.exists("src"), "src directory should exist"
    assert os.path.exists("data"), "data directory should exist"

def test_placeholder():
    """Always passes to ensure CI works."""
    assert True