# FRED: Ocean Cleanup - Test Suite

This directory contains a comprehensive, professional-grade pytest test suite for the FRED: Ocean Cleanup game. The suite is designed for **headless, automated testing** in CI/CD environments with zero human interaction required.

## 🚀 Quick Start

### Installation

Install the development dependencies using `uv`:

```bash
# Install dev dependencies (pytest, pytest-cov, pytest-randomly)
uv add --dev pytest pytest-cov pytest-randomly
```

### Running Tests

Execute the test suite in headless mode with coverage reporting:

```bash
# Run all tests with coverage
SDL_VIDEODRIVER=dummy uv run pytest --cov --cov-report=term-missing

# Run with verbose output
SDL_VIDEODRIVER=dummy uv run pytest -v

# Run specific test file
SDL_VIDEODRIVER=dummy uv run pytest tests/test_physics.py

# Run with multiple random seeds
SDL_VIDEODRIVER=dummy uv run pytest --randomly-seed=42

# Run tests in parallel (if pytest-xdist installed)
SDL_VIDEODRIVER=dummy uv run pytest -n auto
```

For convenience, you can also use the project script (if configured):

```bash
uv run test
```

## 📁 Test Structure

```
tests/
├── conftest.py              # Core fixtures and test utilities
├── test_physics.py          # Physics and movement tests
├── test_scoring.py          # Scoring logic tests
├── test_bottle_collection.py # Bottle spawning and collection tests
├── test_game_state.py       # State machine and UI flow tests
├── test_integration.py      # Integration and full game simulation tests
└── README.md               # This documentation
```

## 🔧 Core Fixtures

The test suite provides powerful fixtures for deterministic testing:

### `env_headless`
- **Scope**: Session (auto-use)
- **Purpose**: Ensures SDL runs in headless mode without graphics
- **Usage**: Automatically applied to all tests

### `pygame_init`
- **Scope**: Session
- **Purpose**: Initializes pygame once for entire test session
- **Usage**: Dependency for game-related fixtures

### `rng_seed`
- **Scope**: Function (parametrized: 42, 1337, 2024)
- **Purpose**: Seeds random module for deterministic tests
- **Usage**: Tests run multiple times with different seeds

### `time_controller`
- **Scope**: Function
- **Purpose**: Mock time control for precise timing tests
- **API**:
  - `tc.now()`: Get current mock time in ms
  - `tc.advance(ms)`: Advance mock clock
  - `tc.patch_pygame_time()`: Context manager for time mocking

### `game_factory`
- **Scope**: Function
- **Purpose**: Creates isolated game worlds for testing
- **Parameters**:
  - `world_size`: Tuple of (width, height)
  - `player_pos`: Initial player position
  - `player_angle`: Initial player angle
  - `bottle_positions`: List of bottle positions
  - `seed`: RNG seed for deterministic spawning

## 🎯 Test Coverage

### Physics & Movement (`test_physics.py`)
- ✅ Differential thrust mechanics (left/right/both)
- ✅ Momentum conservation and drag physics
- ✅ Boundary collision detection and response
- ✅ Physics stability with various delta times
- ✅ No tunneling at high speeds

### Scoring Logic (`test_scoring.py`)
- ✅ Single propeller scoring (1 point/second)
- ✅ Dual propeller scoring (2 points/second)
- ✅ No scoring when coasting
- ✅ Precise timing with fractional seconds
- ✅ Complex interleaved thrust patterns

### Bottle Collection (`test_bottle_collection.py`)
- ✅ Deterministic spawning with seeds
- ✅ Collection on player-bottle collision
- ✅ Bottles remaining counter updates
- ✅ No double-collection of same bottle
- ✅ Game ends when last bottle collected

### Game State Flow (`test_game_state.py`)
- ✅ State transitions (START → PLAYING → END)
- ✅ UI data integrity during gameplay
- ✅ Score and bottles remaining synchronization
- ✅ Complete game flow from start to finish
- ✅ State persistence across transitions

### Integration Tests (`test_integration.py`)
- ✅ Controlled multi-tick game sequences
- ✅ Complex movement and collection patterns
- ✅ Full game simulations (speedrun, efficiency)
- ✅ Property-based testing for invariants
- ✅ Refactoring recommendations for testability

## 🏆 Test Principles

1. **Headless & Automated**: All tests run without GUI using `SDL_VIDEODRIVER=dummy`
2. **Deterministic**: Random seeds and time control ensure repeatable results
3. **Robust**: Uses `pytest.approx()` for floating-point comparisons
4. **Isolated**: Each test gets a fresh game world via fixtures
5. **Fast**: Mock time control allows instant "time travel" in tests

## 🔍 Key Testing Patterns

### Time Control Example
```python
def test_timed_sequence(game_factory, time_controller):
    game = game_factory()
    with time_controller.patch_pygame_time():
        # Advance time precisely
        time_controller.advance(500)  # 500ms forward
        # Test time-dependent behavior
```

### Deterministic Random Testing
```python
def test_with_seed(game_factory, rng_seed):
    # Test runs 3 times with seeds: 42, 1337, 2024
    game = game_factory(seed=rng_seed)
    # Behavior is deterministic for each seed
```

### Physics Assertions
```python
# Use custom assertions for vectors and angles
assert_vector_equal(player.velocity, expected, tolerance=0.01)
assert_angle_equal(player.angle, 90.0, tolerance=0.1)

# Use pytest.approx for scores
assert pytest.approx(game.score, abs=0.01) == expected_score
```

## 🚧 Refactoring Recommendations

The test suite identifies areas where the game code could be more testable:

1. **Clock Injection**: Game class should accept a clock parameter for easier time mocking
2. **RNG Injection**: Bottle spawning should accept an RNG instance for deterministic testing
3. **State Validation**: State machine could benefit from transition history tracking

These are documented in `test_integration.py::TestRefactoringRecommendations`.

## 📊 Coverage Goals

The test suite aims for high coverage of critical game systems:

- Physics engine: >95% coverage
- Scoring system: >95% coverage
- Collision detection: >90% coverage
- State management: >90% coverage
- Integration scenarios: Key user journeys tested

Run coverage report:
```bash
SDL_VIDEODRIVER=dummy uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## 🐛 Debugging Tests

For debugging failing tests:

```bash
# Run with print statements visible
SDL_VIDEODRIVER=dummy uv run pytest -s

# Run with debugger on failure
SDL_VIDEODRIVER=dummy uv run pytest --pdb

# Run specific test with maximum verbosity
SDL_VIDEODRIVER=dummy uv run pytest tests/test_physics.py::TestDifferentialThrust::test_left_thrust_only_turns_right -vv
```

## 📝 Adding New Tests

When adding new tests:

1. Use appropriate fixtures for setup
2. Follow naming convention: `test_<feature>_<scenario>`
3. Group related tests in classes
4. Use parametrize for testing multiple inputs
5. Document complex test scenarios with comments
6. Ensure tests are deterministic and headless

## 🔄 Continuous Integration

For CI/CD integration, use:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  env:
    SDL_VIDEODRIVER: dummy
    SDL_AUDIODRIVER: dummy
  run: |
    uv pip install -e .
    uv add --dev pytest pytest-cov pytest-randomly
    uv run pytest --cov --cov-report=xml --cov-report=term
```

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pygame Testing Guide](https://www.pygame.org/wiki/UnitTests)
- [Property-Based Testing](https://hypothesis.readthedocs.io/)