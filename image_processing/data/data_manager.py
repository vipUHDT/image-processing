import h5py
import numpy as np
import cv2
import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class ImageDataset:
    name: str
    shape: tuple[int]
    dtype: str

class DataManager:
    def __init__(
        self,
        filename: str = "flight.hdf5",
        image_datasets: Optional[list[ImageDataset]] = None
    ):
        self.filename = filename
        self.file = None
        self.image_datasets = image_datasets

    # ---------- helpers ----------
    @staticmethod
    def _read_str_dset(dset) -> np.ndarray:
        """Read a 1-D string dataset as np.ndarray[str]; fallback if needed."""
        try:
            return dset.asstr()[:]  # preferred (string dtype)
        except TypeError:
            raw = dset[:]
            return np.array(
                [x.decode("utf-8") if isinstance(x, (bytes, bytearray)) else str(x) for x in raw],
                dtype=object
            )

    # ---------- init ----------
    def initialize(self):
        """Creates camera datasets + two-key/value string arrays for metadata and detections."""
        self.file   = h5py.File(self.filename, "a")
        self.cdata  = self.file.require_group("camera")
        self.cidata = self.cdata.require_group("images")


        if self.image_datasets:
            for image_dataset in self.image_datasets:
                if image_dataset.name not in self.cidata:
                    self.cidata.create_dataset(
                        image_dataset.name,
                        shape=(0, *image_dataset.shape),
                        maxshape=(None, *image_dataset.shape),
                        dtype=image_dataset.dtype,
                        chunks=(1, *image_dataset.shape),
                        compression="gzip",
                        shuffle=True,
                    )

        # ---------- Top-level metadata as two plain string datasets ----------
        str_t = h5py.string_dtype(encoding="utf-8")

        if "metadata_keys" not in self.file:
            self.file.create_dataset(
                "metadata_keys", shape=(0,), maxshape=(None,),
                dtype=str_t, chunks=(64,), compression="gzip", shuffle=True
            )
        if "metadata_values" not in self.file:
            self.file.create_dataset(
                "metadata_values", shape=(0,), maxshape=(None,),
                dtype=str_t, chunks=(64,), compression="gzip", shuffle=True
            )
        self.meta_keys = self.file["metadata_keys"]
        self.meta_vals = self.file["metadata_values"]

        # sanity checks (metadata)
        if self.meta_keys.shape[0] != self.meta_vals.shape[0]: # type: ignore
            raise RuntimeError("metadata_keys and metadata_values length mismatch")
        try:
            _ = self.meta_keys.asstr(); _ = self.meta_vals.asstr() # type: ignore
        except TypeError:
            raise RuntimeError(
                "metadata_* are not string-typed datasets. Delete/migrate to UTF-8 vlen strings."
            )

        if "detections_keys" not in self.cdata:
            self.cdata.create_dataset(
                "detections_keys", shape=(0,), maxshape=(None,),
                dtype=str_t, chunks=(64,), compression="gzip", shuffle=True
            )
        if "detections_values" not in self.cdata:
            self.cdata.create_dataset(
                "detections_values", shape=(0,), maxshape=(None,),
                dtype=str_t, chunks=(64,), compression="gzip", shuffle=True
            )

        self.det_keys = self.cdata["detections_keys"]
        self.det_vals = self.cdata["detections_values"]

        # sanity checks (detections)
        if self.det_keys.shape[0] != self.det_vals.shape[0]: # type: ignore
            raise RuntimeError("detections_keys and detections_values length mismatch")
        try:
            _ = self.det_keys.asstr(); _ = self.det_vals.asstr() # type: ignore
        except TypeError:
            raise RuntimeError(
                "detections_* are not string-typed datasets. Delete/migrate to UTF-8 vlen strings."
            )

        return self.cdata

    # ---------- top-level metadata ops ----------
    def add_metadata(self, key: str, value: str):
        keys = self._read_str_dset(self.meta_keys)
        where = np.where(keys == key)[0]
        if where.size:
            self.meta_vals[where[0]] = value  # type: ignore
        else:
            n = self.meta_keys.shape[0]  # type: ignore
            self.meta_keys.resize((n + 1,)); self.meta_vals.resize((n + 1,))  # type: ignore
            self.meta_keys[n] = key; self.meta_vals[n] = value  # type: ignore

    def get_metadata_value(self, key: str) -> str:
        keys = self._read_str_dset(self.meta_keys)
        vals = self._read_str_dset(self.meta_vals)
        where = np.where(keys == key)[0]
        if not where.size:
            raise KeyError(f"Key '{key}' not found. Existing keys: {list(keys)}")
        return vals[where[0]]  # type: ignore

    def list_metadata(self):
        keys = self._read_str_dset(self.meta_keys)
        vals = self._read_str_dset(self.meta_vals)
        for k, v in zip(keys, vals):
            print(f"{k} = {v}")

    # ---------- detections ops (datasets, like metadata) ----------
    def add_detection(self, key: str, value: str):
        keys = self._read_str_dset(self.det_keys)
        where = np.where(keys == key)[0]
        if where.size:
            self.det_vals[where[0]] = value  # type: ignore
        else:
            n = self.det_keys.shape[0]  # type: ignore
            self.det_keys.resize((n + 1,)); self.det_vals.resize((n + 1,))  # type: ignore
            self.det_keys[n] = key; self.det_vals[n] = value  # type: ignore

    def get_detection_value(self, key: str) -> str:
        keys = self._read_str_dset(self.det_keys)
        vals = self._read_str_dset(self.det_vals)
        where = np.where(keys == key)[0]
        if not where.size:
            raise KeyError(f"[detections] Key '{key}' not found. Existing keys: {list(keys)}")
        return vals[where[0]]  # type: ignore

    def list_detections(self):
        keys = self._read_str_dset(self.det_keys)
        vals = self._read_str_dset(self.det_vals)
        for k, v in zip(keys, vals):
            print(f"[detections] {k} = {v}")

    # ---------- append frames ----------
    def append_rgb(self, frame: np.ndarray):
        self.append_frame("rgb", frame)
       
    def append_ir(self, frame: np.ndarray):
        self.append_frame("ir", frame)

    def append_frame(self, dataset_name: str, frame: np.ndarray):
        if self.cidata[dataset_name]:
            d = self.cidata[dataset_name]
            if frame.shape != d.shape[1:]:
                raise ValueError(f"Frame for {dataset_name} must be {d.shape[1:]} but got {frame.shape}")
            else:
                n = d.shape[0]
                d.resize((n+1, *d.shape[1:]))
                d[n, ...] = frame.astype(d.dtype, copy=False)


    # ---------- close ----------
    def close(self):
        if self.file:
            self.file.flush()
            self.file.close()
            self.file = None



