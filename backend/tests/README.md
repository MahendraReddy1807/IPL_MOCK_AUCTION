# Test Suite for IPL Mock Auction Arena

## Overview

This directory contains property-based tests using Hypothesis to validate the correctness properties defined in the design document.

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_room_properties.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## Test Files

### test_room_properties.py
- **Property 4: Room capacity constraints** - Validates that all created rooms have min_users=5 and max_users=10

### test_team_properties.py
- **Property 10: Purse amount validation** - Validates that the system rejects non-positive purse amounts and accepts positive values

## Property-Based Testing

All tests use Hypothesis to generate random test cases (100 examples per test by default). This ensures comprehensive coverage across the input space.

### Configuration
- Each test runs 100 iterations with randomly generated inputs
- Tests suppress the `function_scoped_fixture` health check to work with pytest fixtures
- Custom strategies are used to generate valid domain objects

## Validation Functions

The `app.utils.validation` module contains validation functions that will be used by the service layer:
- `validate_purse_amount(purse_amount)` - Validates purse is a positive number
- `validate_username(username)` - Validates username is non-empty
- `validate_team_name(team_name)` - Validates team name is non-empty

These functions are tested by the property-based tests and will be integrated into the service layer in future tasks.
