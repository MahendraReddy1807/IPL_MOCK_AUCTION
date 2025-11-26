"""Test runner script."""
import sys
import subprocess


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running IPL Mock Auction Arena Tests")
    print("=" * 60)
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        capture_output=False
    )
    
    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
