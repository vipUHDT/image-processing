import h5py
import numpy as np
import cv2
import os

class DatasetWriter:
    def __init__(
        self,
        filename: str = "flight.hdf5",
        rgbh: int = 1080, rgbw: int = 1920,
        irh: int = 480,  irw: int = 640
    ):
        self.filename = filename
        self.file = None
        self.rgbh, self.rgbw = rgbh, rgbw
        self.irh, self.irw   = irh, irw

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

        # ---- RGB: (N,H,W,3) uint8
        if "rgb" not in self.cidata:
            self.cidata.create_dataset(
                "rgb",
                shape=(0, self.rgbh, self.rgbw, 3),
                maxshape=(None, self.rgbh, self.rgbw, 3),
                dtype="uint8",
                chunks=(1, self.rgbh, self.rgbw, 3),
                compression="gzip",
                shuffle=True,
            )

        # ---- IR: (N,H,W) float32
        if "ir" not in self.cidata:
            self.cidata.create_dataset(
                "ir",
                shape=(0, self.irh, self.irw),
                maxshape=(None, self.irh, self.irw),
                dtype="float32",
                chunks=(1, self.irh, self.irw),
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
        d = self.cidata["rgb"]
        if frame.shape != (self.rgbh, self.rgbw, 3):
            raise ValueError(f"RGB frame must be {(self.rgbh, self.rgbw, 3)}; got {frame.shape}")
        n = d.shape[0]; d.resize((n + 1, self.rgbh, self.rgbw, 3))  # type: ignore
        d[n, ...] = frame.astype(np.uint8, copy=False)  # type: ignore

    def append_ir(self, frame: np.ndarray):
        d = self.cidata["ir"]
        if frame.shape != (self.irh, self.irw):
            raise ValueError(f"IR frame must be {(self.irh, self.irw)}; got {frame.shape}")
        n = d.shape[0]; d.resize((n + 1, self.irh, self.irw))  # type: ignore
        d[n, ...] = frame.astype(np.float32, copy=False)  # type: ignore

    # ---------- close ----------
    def close(self):
        if self.file:
            self.file.flush()
            self.file.close()
            self.file = None


# ------------------- MAIN TEST -------------------
if __name__ == "__main__":
    w = DatasetWriter("flight.hdf5", rgbh=1080, rgbw=1920, irh=480, irw=640)
    w.initialize()

    # top-level metadata
    w.add_metadata("time", "67")
    w.add_metadata("date", "67")
    w.add_metadata("status", "OK")

    # detections (now datasets under /camera)
    w.add_detection("model", "yolov8")
    w.add_detection("threshold", "0.35")
    w.add_detection("nms", "0.50")

    print("status =", w.get_metadata_value("status"))
    print("[detections] model =", w.get_detection_value("model"))

    print("\nAll metadata:")
    w.list_metadata()
    print("\nAll detections:")
    w.list_detections()

    # add images only if files exist
    if os.path.exists("rgb.jpg"):
        bgr = cv2.imread("rgb.jpg", cv2.IMREAD_COLOR)
        if bgr is not None:
            bgr = cv2.resize(bgr, (w.rgbw, w.rgbh))
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            w.append_rgb(rgb); print("✅ Added RGB image")
        else:
            print("⚠️ Could not read rgb.jpg")
    else:
        print("⚠️ rgb.jpg not found; skipping")

    if os.path.exists("ir.jpg"):
        ir_gray = cv2.imread("ir.jpg", cv2.IMREAD_GRAYSCALE)
        if ir_gray is not None:
            ir_gray = cv2.resize(ir_gray, (w.irw, w.irh))
            w.append_ir(ir_gray.astype(np.float32)); print("✅ Added IR image")
        else:
            print("⚠️ Could not read ir.jpg")
    else:
        print("⚠️ ir.jpg not found; skipping")

    print("\nRGB shape:", w.file["/camera/images/rgb"].shape)  # type: ignore
    print("IR  shape:", w.file["/camera/images/ir"].shape)     # type: ignore

    w.close()
    print("\n✅ Done — /camera now has detections_keys/detections_values datasets (string, like metadata).")
