import h5py
import numpy as np
import cv2
import os

class DatasetWriter:
    def __init__(
            self,
            filename: str = "flight.hdf5",
            rgbh: int = 1080,
            rgbw: int = 1920,
            irh: int = 480,
            irw: int = 640):
        self.filename = filename
        self.file = None
        self.rgbh, self.rgbw = rgbh, rgbw
        self.irh, self.irw   = irh, irw

    # ---------- Initialization ----------
    def initialize(self):
        """Creates camera datasets and /metadata table (key, value[str])."""
        self.file   = h5py.File(self.filename, "a")
        self.cdata  = self.file.require_group("camera")
        self.cidata = self.cdata.require_group("images")
        self.cddata = self.cdata.require_group("detections")

        # ---- RGB dataset: (N,H,W,3) uint8 ----
        if "rgb" not in self.cidata:
            self.cidata.create_dataset(
                "rgb",
                shape=(0, self.rgbh, self.rgbw, 3),
                maxshape=(None, self.rgbh, self.rgbw, 3),
                dtype="uint8",
                chunks=(1, self.rgbh, self.rgbw, 3),
                compression="gzip",
                shuffle=True
            )

        # ---- IR dataset: (N,H,W) float32 ----
        if "ir" not in self.cidata:
            self.cidata.create_dataset(
                "ir",
                shape=(0, self.irh, self.irw),
                maxshape=(None, self.irh, self.irw),
                dtype="float32",
                chunks=(1, self.irh, self.irw),
                compression="gzip",
                shuffle=True
            )

        # ---------- Metadata table: (key, value) both strings ----------
        str_t = h5py.string_dtype(encoding="utf-8")
        meta_dt = np.dtype([("key", str_t), ("value", str_t)])

        # Prevent conflict if /metadata is a group
        if "metadata" in self.file and isinstance(self.file["metadata"], h5py.Group):
            raise RuntimeError("'/metadata' exists as a group — delete or rename it first.")

        if "metadata" not in self.file:
            self.file.create_dataset(
                "metadata",
                shape=(0,),
                maxshape=(None,),
                dtype=meta_dt,
                chunks=(64,),
                compression="gzip",
                shuffle=True
            )

        self.meta = self.file["metadata"]

        # Validate dtype if file existed
        expected_names = ("key", "value")
        if tuple(self.meta.dtype.names) != expected_names: #type: ignore
            raise RuntimeError(
                f"/metadata dtype mismatch. Found {self.meta.dtype.names}, expected {expected_names}. " #type: ignore
                "Delete or migrate the file."
            )
        return self.cdata

    def add_dectection(self):
        pass

    @staticmethod
    def _decode_one(x) -> str:
        return x.decode("utf-8") if isinstance(x, (bytes, bytearray)) else str(x)

    def _keys_as_str(self) -> np.ndarray:
        """Return all keys as str array (decode UTF-8 if needed)."""
        raw = self.meta[:]["key"]  # compound field slice #type: ignore
        return np.array([self._decode_one(k) for k in raw], dtype=object) #type: ignore

    def _vals_as_str(self) -> np.ndarray:
        """Return all values as str array (decode UTF-8 if needed)."""
        raw = self.meta[:]["value"] #type: ignore
        return np.array([self._decode_one(v) for v in raw], dtype=object) #type: ignore

    # ---------- Add or update metadata ----------
    def add_metadata(self, key: str, value: str):
        """Add or update a (key, value[str]) record in /metadata."""
        meta = self.meta
        keys = self._keys_as_str()
        where = np.where(keys == key)[0]

        row = np.empty(1, dtype=meta.dtype) #type: ignore
        row["key"][0] = key #type: ignore
        row["value"][0] = value #type: ignore

        if where.size:
            meta[where[0]] = row[0]  # update existing #type: ignore
        else:
            n = meta.shape[0] #type: ignore
            meta.resize((n + 1,)) #type: ignore
            meta[n] = row[0]         # append new #type: ignore

    # ---------- Retrieve ----------
    def get_metadata_value(self, key: str) -> str:
        """Return string value for given key."""
        meta = self.meta
        keys = self._keys_as_str()
        where = np.where(keys == key)[0]
        if not where.size:
            raise KeyError(f"Key '{key}' not found in /metadata. Existing keys: {list(keys)}")
        v = meta[:]["value"][where[0]] #type: ignore
        return self._decode_one(v)

    # ---------- Append RGB/IR ----------
    def append_rgb(self, frame: np.ndarray):
        """Append one RGB frame."""
        d = self.cidata["rgb"]
        n = d.shape[0] #type: ignore
        d.resize((n + 1, self.rgbh, self.rgbw, 3)) #type: ignore
        d[n, ...] = frame.astype(np.uint8) #type: ignore

    def append_ir(self, frame: np.ndarray):
        """Append one IR frame."""
        d = self.cidata["ir"]
        n = d.shape[0] #type: ignore
        d.resize((n + 1, self.irh, self.irw)) #type: ignore
        d[n, ...] = frame.astype(np.float32) #type: ignore

    # ---------- Close ----------
    def close(self):
        if self.file:
            self.file.flush()
            self.file.close()
            self.file = None


# ---------- MAIN TEST ----------
if __name__ == "__main__":
    w = DatasetWriter("flight.hdf5", rgbh=1080, rgbw=1920, irh=480, irw=640)
    w.initialize()

    # --- Add metadata entries (strings)
    w.add_metadata("session_id", "67")
    w.add_metadata("frames_captured", "12")
    w.add_metadata("temperature_C", "27")
    w.add_metadata("operator", "BIG Boss")
    w.add_metadata("status", "OK")

    # --- Retrieve one
    print("frames_captured =", w.get_metadata_value("frames_captured"))

    # --- List all metadata (robust decode)
    keys = w._keys_as_str()
    vals = w._vals_as_str()
    print("\nAll metadata entries:")
    for k, v in zip(keys, vals):
        print(f"{k} = {v}")

    # RGB
    rgb_path = "bus.jpg"
    if os.path.exists(rgb_path):
        bgr = cv2.imread(rgb_path, cv2.IMREAD_COLOR) #type: ignore
        bgr = cv2.resize(bgr, (w.rgbw, w.rgbh))
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        w.append_rgb(rgb)
    else:
        rgb = (np.random.rand(w.rgbh, w.rgbw, 3) * 255).astype(np.uint8)
        w.append_rgb(rgb)

    # IR
    ir_path = "ir.jpg"
    if os.path.exists(ir_path):
        ir_gray = cv2.imread('ir.jpg', cv2.IMREAD_GRAYSCALE) #type: ignore
        ir_gray = cv2.resize(ir_gray, (w.irw, w.irh))
        ir = ir_gray.astype(np.float32)
        w.append_ir(ir)
    else:
        ir  = (np.random.rand(w.irh,  w.irw) * 255).astype(np.float32)
        w.append_ir(ir)

    print("\nRGB dataset shape:", w.file["/camera/images/rgb"].shape) #type: ignore
    print("IR  dataset shape:", w.file["/camera/images/ir"].shape) #type: ignore
    value = w.get_metadata_value("status")
    print(value)
    w.close()
    print("\n✅ Done")

