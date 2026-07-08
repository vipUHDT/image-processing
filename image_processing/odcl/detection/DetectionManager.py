"""Threaded detection pipeline: queues images, runs inference, and georeferences results."""

import logging
import threading
from queue import Empty, Queue
from typing import Optional

from sahi.prediction import PredictionResult

from image_processing import PlatformState, QueuedImage
from image_processing.camera import CameraMetadata
from image_processing.odcl.Localize import Georeference_Engine, haversine

from .Detection import Detection, DetectionModelResult, Detector
from .SahiConfig import ModelConfig

LOGGER = logging.getLogger(__name__)


class DetectionManager:
    """
    Run object detection on queued images in persistent worker threads.

    Each worker loads the detection model once at startup and then processes
    images from the queue for the manager's lifetime. Detections are
    georeferenced (when an engine and camera metadata are configured),
    de-duplicated by GPS proximity, and appended to ``detections`` and
    ``results`` as soon as they are accepted.

    Workers are started lazily by ``processQueuedImages`` (or explicitly with
    ``start``) and stopped with ``stop``.

    Parameters
    ----------
    detection_model_config : ModelConfig, optional
        Model configuration passed to each ``Detector``.
    camera_metadata : CameraMetadata, optional
        Camera intrinsics used for georeferencing.
    georeference_engine : Georeference_Engine, optional
        Engine used to convert pixel coordinates to GPS coordinates.
    """

    def __init__(
        self,
        detection_model_config: Optional[ModelConfig] = None,
        camera_metadata: CameraMetadata | None = None,
        georeference_engine: Georeference_Engine | None = None,
    ):
        self.detection_model_config = detection_model_config
        self.image_queue = Queue()
        self.gps_callback = None

        self.detections: list[Detection] = []
        self.results: list[DetectionModelResult] = []
        self._lock = threading.Lock()

        self.workers = 5
        self._worker_threads: list[threading.Thread] = []
        self._stop_event = threading.Event()

        self.duplicate_threshold = 2  # meters
        self.camera: CameraMetadata | None = camera_metadata
        self.georeference_engine = georeference_engine

    def setGPSCallback(self, callback):
        """Register a callable invoked with each new detection's GPS coordinates."""
        self.gps_callback = callback

    # ---------- worker lifecycle ----------
    def start(self):
        """Start the worker threads if they are not already running."""
        if self._worker_threads:
            return
        self._stop_event.clear()
        for i in range(self.workers):
            t = threading.Thread(
                target=self._workerLoop,
                daemon=True,
                name=f"DetectionManager-{i}",
            )
            t.start()
            self._worker_threads.append(t)

    def stop(self, wait: bool = True):
        """Signal the workers to exit and optionally wait for them."""
        self._stop_event.set()
        if wait:
            for t in self._worker_threads:
                t.join(timeout=5)
        self._worker_threads = []

    def _workerLoop(self):
        """Load the model once, then process queued images until stopped."""
        detector = Detector(self.detection_model_config)
        try:
            detector.loadModel()
        except Exception:
            LOGGER.exception("Detection worker failed to load model; exiting")
            return
        while not self._stop_event.is_set():
            try:
                queued_image = self.image_queue.get(timeout=0.2)
            except Empty:
                continue
            try:
                self.ODCL(detector, queued_image.image, queued_image.platform_state)
            except Exception:
                LOGGER.exception("Detection worker failed to process image")
            finally:
                self.image_queue.task_done()

    # ---------- pipeline ----------
    def queueImage(self, image: QueuedImage):
        """Add an image (with platform state) to the processing queue."""
        self.image_queue.put(image)

    def processQueuedImages(self):
        """Ensure the worker threads are running (kept for backward compatibility)."""
        self.start()

    def update(self):
        """No-op kept for backward compatibility.

        Detections and results are now appended to ``detections`` and
        ``results`` directly by the workers as they are produced.
        """

    def ODCL(self, detector: Detector, image, platform_state):
        """Run object detection, classification, and localization on one image."""
        results = detector.run(image)
        if isinstance(results, PredictionResult):
            detection_model_result, detections = detector.parseResults(results)
            self.addResult(detection_model_result)
            self.addDetections(detections, platform_state)

    def addResult(self, result: DetectionModelResult):
        """Record a model result."""
        with self._lock:
            self.results.append(result)

    def addDetection(self, detection: Detection, platform_state: PlatformState):
        """Georeference a detection and record it unless it duplicates an existing one."""
        if isinstance(self.georeference_engine, Georeference_Engine) and isinstance(self.camera, CameraMetadata):
            detection.gps_coords = self.georeference(
                detection.pixel_coords,
                platform_state,
                self.camera,
            )

        with self._lock:
            if self._isDuplicate(detection):
                return
            LOGGER.debug("New detection at %s", detection.gps_coords)
            self.detections.append(detection)
        if self.gps_callback:
            self.gps_callback(detection.gps_coords)

    def addDetections(self, detections: list[Detection], platform_state: PlatformState):
        """Add multiple detections via ``addDetection``."""
        for detection in detections:
            self.addDetection(detection, platform_state)

    def _isDuplicate(self, detection: Detection) -> bool:
        """Return True if a known detection lies within ``duplicate_threshold`` meters.

        Must be called with ``self._lock`` held so the check and the caller's
        append are atomic with respect to other workers.
        """
        if not detection.gps_coords:
            return False
        for existing_detection in self.detections:
            if not existing_detection.gps_coords:
                continue
            distance = haversine(
                detection.gps_coords[0],
                detection.gps_coords[1],
                existing_detection.gps_coords[0],
                existing_detection.gps_coords[1],
            )
            if abs(distance) < self.duplicate_threshold:
                return True
        return False

    def checkForDuplicates(self, detection: Detection) -> bool:
        """Return True if a known detection lies within ``duplicate_threshold`` meters."""
        with self._lock:
            return self._isDuplicate(detection)

    # ---------- georeferencing ----------
    def setGeoreferenceEngine(self, georeference_backend, altitude_offset=0):
        """Create the georeference engine for the given backend name."""
        self.georeference_engine = Georeference_Engine(georeference_backend, altitude_offset)

    def georeference(self, target_pixel_coordinates, platform_state, camera_metadata):
        """Convert pixel coordinates to GPS via the configured engine, or None."""
        if self.georeference_engine:
            return self.georeference_engine.georeference(
                target_pixel_coordinates, platform_state, camera_metadata
            )

    # ---------- accessors ----------
    def getAllDetections(self):
        """Return all collected detections."""
        with self._lock:
            return list(self.detections)

    def filterByClassification(self, classification: str):
        """Return collected detections with the given classification label."""
        with self._lock:
            return [d for d in self.detections if d.classification == classification]

    def filterByConfidence(self, threshold: float):
        """Return collected detections with confidence at or above ``threshold``."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        with self._lock:
            return [d for d in self.detections if d.confidence >= threshold]

    def clearDetections(self):
        """Remove all collected detections."""
        with self._lock:
            self.detections.clear()
