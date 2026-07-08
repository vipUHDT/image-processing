"""Unit tests for the HDF5-backed DataManager."""

import numpy as np
import pytest

from image_processing.data.data_manager import DataManager, ImageDataset


@pytest.fixture
def manager(tmp_path):
    dm = DataManager(
        filename=str(tmp_path / "flight.hdf5"),
        image_datasets=[ImageDataset(name="rgb", shape=(8, 8, 3), dtype="uint8")],
    )
    dm.initialize()
    yield dm
    dm.close()


def test_requires_initialize(tmp_path):
    dm = DataManager(filename=str(tmp_path / "x.hdf5"))
    with pytest.raises(RuntimeError):
        dm.add_metadata("k", "v")


def test_context_manager(tmp_path):
    path = str(tmp_path / "flight.hdf5")
    with DataManager(filename=path) as dm:
        dm.add_metadata("pilot", "uhdt")
        assert dm.get_metadata_value("pilot") == "uhdt"
    assert dm.file is None


def test_metadata_roundtrip_and_overwrite(manager):
    manager.add_metadata("mission", "test-flight")
    manager.add_metadata("mission", "real-flight")
    assert manager.get_metadata_value("mission") == "real-flight"
    assert manager.list_metadata() == {"mission": "real-flight"}


def test_missing_metadata_key_raises(manager):
    with pytest.raises(KeyError):
        manager.get_metadata_value("nope")


def test_detections_roundtrip(manager):
    manager.add_detection("target_1", "21.3,-157.8")
    assert manager.get_detection_value("target_1") == "21.3,-157.8"
    assert manager.list_detections() == {"target_1": "21.3,-157.8"}


def test_append_frame_roundtrip(manager):
    frame = np.arange(8 * 8 * 3, dtype=np.uint8).reshape(8, 8, 3)
    manager.append_rgb(frame)
    stored = manager.cidata["rgb"]
    assert stored.shape == (1, 8, 8, 3)
    assert np.array_equal(stored[0], frame)


def test_append_frame_wrong_shape_raises(manager):
    with pytest.raises(ValueError):
        manager.append_frame("rgb", np.zeros((4, 4, 3), dtype=np.uint8))


def test_append_frame_unknown_dataset_raises(manager):
    with pytest.raises(KeyError):
        manager.append_frame("ir", np.zeros((8, 8, 3), dtype=np.uint8))


def test_persistence_across_reopen(tmp_path):
    path = str(tmp_path / "flight.hdf5")
    datasets = [ImageDataset(name="rgb", shape=(8, 8, 3), dtype="uint8")]
    with DataManager(filename=path, image_datasets=datasets) as dm:
        dm.add_metadata("flight", "one")
        dm.append_rgb(np.zeros((8, 8, 3), dtype=np.uint8))
    with DataManager(filename=path, image_datasets=datasets) as dm:
        assert dm.get_metadata_value("flight") == "one"
        assert dm.cidata["rgb"].shape[0] == 1
