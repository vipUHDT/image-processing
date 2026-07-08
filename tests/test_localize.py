"""Unit tests for the georeferencing backends and Georeference_Engine.

Geometry used throughout: sensor 6.0 x 4.0 mm, focal length 4.0 mm, image
1200 x 800 px, altitude 100 m above ground. The ground footprint is then
150 m x 100 m (altitude * sensor / focal), i.e. 0.125 m per pixel on both
axes.
"""

import math

import pytest

from image_processing import PlatformState
from image_processing.camera import CameraMetadata
from image_processing.odcl.Localize import (
    Georeference_Engine,
    georeference_aeqd,
    georeference_enu,
    georeference_manual,
    georeference_utm,
    haversine,
)

BACKENDS = [georeference_utm, georeference_enu, georeference_aeqd, georeference_manual]

# Honolulu-ish origin.
LAT, LON = 21.3069, -157.8583
ALTITUDE = 100.0
SENSOR_W, SENSOR_H = 6.0, 4.0
PIX_W, PIX_H = 1200, 800
FOCAL = 4.0

CENTER = (PIX_W / 2, PIX_H / 2)
TOP_CENTER = (PIX_W / 2, 0)  # 50 m ahead of the platform
RIGHT_CENTER = (PIX_W, PIX_H / 2)  # 75 m right of the platform


def run(backend, pixel, yaw=0.0, altitude_offset=0.0, lat=LAT, lon=LON):
    return backend(
        pixel, lat, lon, ALTITUDE, altitude_offset, yaw,
        SENSOR_W, SENSOR_H, PIX_W, PIX_H, FOCAL,
    )


def east_north_of(target_lat, target_lon, lat=LAT, lon=LON):
    """Approximate (east, north) meters from the origin to the target."""
    north = haversine(lat, lon, target_lat, lon) * math.copysign(1, target_lat - lat)
    east = haversine(lat, lon, lat, target_lon) * math.copysign(1, target_lon - lon)
    return east, north


@pytest.mark.parametrize("backend", BACKENDS)
def test_center_pixel_maps_to_platform_position(backend):
    target_lat, target_lon = run(backend, CENTER)
    assert haversine(LAT, LON, target_lat, target_lon) < 0.01


@pytest.mark.parametrize("backend", BACKENDS)
def test_top_of_image_is_north_at_yaw_zero(backend):
    """Pixel y grows downward, so the top of the image is ahead (north at yaw 0)."""
    target_lat, target_lon = run(backend, TOP_CENTER, yaw=0.0)
    east, north = east_north_of(target_lat, target_lon)
    assert north == pytest.approx(50.0, rel=0.01)
    assert abs(east) < 1.0  # UTM grid convergence skews axes slightly


@pytest.mark.parametrize("backend", BACKENDS)
def test_right_of_image_is_east_at_yaw_zero(backend):
    target_lat, target_lon = run(backend, RIGHT_CENTER, yaw=0.0)
    east, north = east_north_of(target_lat, target_lon)
    assert east == pytest.approx(75.0, rel=0.01)
    assert abs(north) < 1.0  # UTM grid convergence skews axes slightly


@pytest.mark.parametrize("backend", BACKENDS)
def test_yaw_rotates_clockwise_from_north(backend):
    """At heading 90 (east), a target ahead of the platform lies to its east."""
    target_lat, target_lon = run(backend, TOP_CENTER, yaw=90.0)
    east, north = east_north_of(target_lat, target_lon)
    assert east == pytest.approx(50.0, rel=0.01)
    assert abs(north) < 1.0  # UTM grid convergence skews axes slightly


@pytest.mark.parametrize("backend", BACKENDS)
def test_altitude_offset_shrinks_footprint(backend):
    """Halving the height above ground halves the ground offset."""
    target_lat, target_lon = run(backend, TOP_CENTER, altitude_offset=50.0)
    _, north = east_north_of(target_lat, target_lon)
    assert north == pytest.approx(25.0, rel=0.01)


def test_backends_agree():
    for pixel in [TOP_CENTER, RIGHT_CENTER, (100, 700)]:
        results = [run(backend, pixel, yaw=37.0) for backend in BACKENDS]
        reference = results[0]
        for other in results[1:]:
            assert haversine(*reference, *other) < 1.0


def test_southern_hemisphere_utm():
    target_lat, target_lon = run(georeference_utm, TOP_CENTER, lat=-33.86, lon=151.21)
    east, north = east_north_of(target_lat, target_lon, lat=-33.86, lon=151.21)
    assert north == pytest.approx(50.0, rel=0.01)


def test_engine_unknown_backend_raises():
    with pytest.raises(ValueError):
        Georeference_Engine("nonsense")


def test_engine_uses_constructor_altitude_offset():
    engine = Georeference_Engine("enu", altitude_offset=50.0)
    state = PlatformState(
        altitude=ALTITUDE, latitude=LAT, longitude=LON, pitch=0.0, yaw=0.0, roll=0.0
    )
    metadata = CameraMetadata(SENSOR_W, SENSOR_H, PIX_W, PIX_H, FOCAL)

    target_lat, target_lon = engine.georeference(TOP_CENTER, state, metadata)
    _, north = east_north_of(target_lat, target_lon)
    assert north == pytest.approx(25.0, rel=0.01)

    # An explicit offset overrides the constructor's.
    target_lat, target_lon = engine.georeference(
        TOP_CENTER, state, metadata, altitude_offset=0.0
    )
    _, north = east_north_of(target_lat, target_lon)
    assert north == pytest.approx(50.0, rel=0.01)


def test_haversine_known_distance():
    # One degree of latitude is ~111.2 km.
    assert haversine(0.0, 0.0, 1.0, 0.0) == pytest.approx(111_195, rel=0.01)
    assert haversine(LAT, LON, LAT, LON) == 0.0
