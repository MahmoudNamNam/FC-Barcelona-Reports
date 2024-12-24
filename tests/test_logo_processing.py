import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.logo_processing import load_and_resize_logo

# Test case to check if the logo is found and successfully processed
def test_logo_found():
    encoded_logo = load_and_resize_logo("Barcelona")
    assert encoded_logo is not None, "Logo was not found or processed correctly."

# Test case to check if the function handles missing logos correctly
def test_logo_not_found():
    encoded_logo = load_and_resize_logo("UnknownTeam")
    assert "Error" in encoded_logo, f"Expected error message but got: {encoded_logo}"
