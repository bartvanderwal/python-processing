# Testing Examples

Real-world examples from this zombie survival game project.

## Example 1: Parametrized Tests (Player Movement)

**Module**: `src/entities/player.py`

```python
# Existing tests - GOOD parametrization example
@pytest.mark.parametrize("input,expected", [
    (case1_input, case1_expected),
    (case2_input, case2_expected),
])
def test_player_movement_boundaries(input, expected):
    """Test player stays within screen bounds"""
    player = Player(400, 300, 800, 600)
    # Test movement logic
```

## Example 2: Shared Fixtures in conftest.py

**conftest.py** - Current structure:

```python
"""Shared fixtures for all tests"""

import pytest
import pygame


@pytest.fixture
def game():
    """Create a Game instance for testing."""
    pygame.init()
    game = Game()
    yield game
    pygame.quit()
```

Usage in `tests/test_game.py`:

```python
def test_initial_state(game):
    """Test game starts in MENU state"""
    assert game.state == GameState.MENU
```

**Why this works**:
- `game` fixture initialized pygame once
- Automatically available to all test files
- Cleanup handled automatically (`yield` + teardown)
- No duplication across test files

## Example 3: Minimal Mocking - Only External Dependencies

**BAD Example** (over-mocking):

```python
def test_zombie_chase_player(mocker):
    # ❌ Don't mock internal game logic!
    mock_zombie = mocker.patch('entities.zombie.Zombie')
    mock_player = mocker.patch('entities.player.Player')
    # This test passes even if the real code is broken!
```

**GOOD Example** (real objects):

```python
def test_zombie_chase_player():
    """Test zombie moves toward player position"""
    # ✅ Use real objects - catches actual bugs
    zombie = Zombie(0, 0)
    initial_x, initial_y = zombie.x, zombie.y

    # Zombie should move toward player at (100, 100)
    zombie.update(1.0, player_x=100, player_y=100)

    assert zombie.x > initial_x  # Moved right
    assert zombie.y > initial_y  # Moved down
```

**When TO mock** (external dependency):

```python
def test_sprite_loading_failure(mocker):
    """Test fallback when sprite file doesn't exist"""
    # ✅ Mock file I/O - external dependency
    mocker.patch('pygame.image.load', side_effect=FileNotFoundError)

    player = Player(400, 300, 800, 600)
    # Should fallback to circle rendering without crashing
    assert player.sprite_image is None
```

## Example 4: Testing Configuration Classes

**Module**: `src/config.py`

```python
# Dataclass configurations
@dataclass
class PlayerConfig:
    radius: int = 15
    speed: int = 200
    max_health: int = 100
```

**Tests** - Simple but comprehensive:

```python
class TestPlayerConfig:
    """Test player configuration."""

    def test_player_defaults(self):
        """Test player config has expected default values"""
        config = PlayerConfig()
        assert config.radius == 15
        assert config.speed == 200
        assert config.max_health == 100
```

**Why no mocking needed**:
- Pure data structure
- No external dependencies
- Testing real behavior is simple and reliable

## Example 5: Parametrizing Edge Cases

**Testing wave calculation** - Multiple inputs:

```python
@pytest.mark.parametrize("wave,expected_zombies", [
    (1, 3),    # First wave
    (2, 4),    # Exponential growth
    (3, 6),
    (4, 10),
    (5, 15),
    (100, 20), # Cap at max
])
def test_wave_zombie_calculation(game, wave, expected_zombies):
    """Test progressive difficulty formula"""
    assert game.calculate_wave_zombies(wave) == expected_zombies
```

**Benefits**:
- Tests 6 cases with one function
- Easy to add more cases
- Clear what each case tests
- Self-documenting (wave 100 hits cap)

## Example 6: Testing Error Handling

```python
def test_player_death(self):
    """Test player death when health reaches 0"""
    player = Player(400, 300, 800, 600)
    player.take_damage(100)
    assert player.health == 0
    assert not player.is_alive()
```

**With parametrization**:

```python
@pytest.mark.parametrize("damage_amount", [100, 150, 1000])
def test_player_death_various_damage(damage_amount):
    """Test player dies regardless of overkill damage"""
    player = Player(400, 300, 800, 600)
    player.take_damage(damage_amount)
    assert not player.is_alive()
```

## Example 7: Using pytest's Built-in Fixtures

```python
def test_config_serialization(tmp_path):
    """Test saving config to file"""
    # tmp_path is a built-in pytest fixture
    config_file = tmp_path / "config.json"

    config = GameConfig()
    save_config(config, config_file)

    # Read back and verify - no mocking needed!
    loaded = load_config(config_file)
    assert loaded.screen_width == config.screen_width
```

**Built-in fixtures to use**:
- `tmp_path`: Temporary directory (Path object)
- `capsys`: Capture stdout/stderr
- `mocker`: From pytest-mock plugin

## Example 8: Testing Visual Effects (Bug Fix)

**The bug** we fixed earlier:

```python
def test_render_kill_flashes_timer_exceeds_max(game):
    """Test rendering when timer exceeds expected max (edge case bug)."""
    game.kill_flashes = [
        {"x": 100, "y": 100, "radius": 15, "timer": 0.16},  # Over 0.15
        {"x": 200, "y": 200, "radius": 15, "timer": 1.0},   # Way over
    ]
    # Should not raise ValueError about invalid color
    game.render_kill_flashes()
```

**Why this test is valuable**:
- Caught a real bug (alpha > 255)
- Tests edge case (timer slightly over max)
- No mocking - tests real rendering logic
- Prevents regression

## Key Patterns Summary

### ✅ Good Practices

```python
# Parametrize similar cases
@pytest.mark.parametrize("input,expected", cases)

# Use real objects
player = Player(400, 300, 800, 600)

# Share fixtures in conftest.py
@pytest.fixture
def game(): ...

# Test one behavior per test
def test_zombie_moves_toward_player():

# Use built-in fixtures
def test_with_temp_file(tmp_path):
```

### ❌ Avoid

```python
# Don't mock internal logic
mocker.patch('src.internal.function')

# Don't duplicate fixtures
# (put in conftest.py instead)

# Don't test multiple behaviors in one test
def test_everything(): # Too broad!

# Don't over-specify mocks
# (makes tests brittle)
```
