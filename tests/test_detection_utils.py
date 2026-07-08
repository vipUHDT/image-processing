"""Unit tests for Detection bounding-box utilities and the Detection dataclass."""

import numpy as np
import pytest

from image_processing.odcl.detection.Detection import Detection, Detector


@pytest.fixture
def detector():
    d = Detector()
    d.backend = "sahi"  # bounding-box helpers are backend-gated
    return d


class TestAdjustBoundingBox:
    def test_pads_exactly_by_requested_amount(self, detector):
        assert detector.adjustBoundingBox((50, 50, 100, 100), 5, 640, 480) == (45, 45, 105, 105)

    def test_zero_padding_is_identity(self, detector):
        assert detector.adjustBoundingBox((50, 50, 100, 100), 0, 640, 480) == (50, 50, 100, 100)

    def test_clamps_to_image_bounds(self, detector):
        assert detector.adjustBoundingBox((2, 3, 638, 478), 10, 640, 480) == (0, 0, 640, 480)

    def test_clamps_each_side_independently(self, detector):
        assert detector.adjustBoundingBox((2, 100, 200, 300), 5, 640, 480) == (0, 95, 205, 305)


class TestGetBoundingBoxCenter:
    def test_center(self, detector):
        assert detector.getBoundingBoxCenter((10, 20, 30, 60)) == (20, 40)

    def test_no_backend_returns_sentinel(self):
        d = Detector()
        assert d.getBoundingBoxCenter((10, 20, 30, 60)) == (-1, -1)


class TestCropDetection:
    def test_crop_shape(self, detector):
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        crop = detector.cropDetection(image, (10, 20, 110, 220))
        assert crop.shape == (200, 100, 3)


class TestDetection:
    def _make(self, confidence):
        image = np.zeros((4, 4, 3), dtype=np.uint8)
        return Detection("person", confidence, (2, 2), image)

    def test_valid_confidence(self):
        detection = self._make(0.9)
        assert detection.confidence == 0.9
        assert detection.get_confidence() == 0.9
        assert detection.gps_coords is None

    @pytest.mark.parametrize("confidence", [-0.1, 1.5])
    def test_invalid_confidence_raises_at_construction(self, confidence):
        with pytest.raises(ValueError):
            self._make(confidence)
