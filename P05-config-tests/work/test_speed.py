"My own tests for minutes_per_km."

import pytest

from orders import minutes_per_km


def test_slow_delivery():
    # 60 min for 6 km is 10 min/km
    assert minutes_per_km(60, 6) == 10.0


def test_negative_distance_raises():
    # negative distance should raise ValueError
    with pytest.raises(ValueError):
        minutes_per_km(30, -3)
