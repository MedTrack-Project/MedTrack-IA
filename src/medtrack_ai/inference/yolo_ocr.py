"""Adaptador da combinação YOLOv8 e EasyOCR usada pelo MedTrack."""

from importlib import import_module
from typing import Any

import numpy as np

from medtrack_ai.domain.models import DetectionResult, ExtractedMedicineData
from medtrack_ai.inference.service import ModelLoadError, require_local_model
from medtrack_ai.inference.text import sanitizar_texto


class YoloOcrInferenceService:
    """Carrega os recursos de IA uma vez e executa inferências síncronas."""

    def __init__(self, *, model_uri: str, model_version: str, device: str, confidence: float):
        self.model_version = model_version
        self.device = device
        self.confidence = confidence
        self._model = self._load_model(model_uri)
        self._reader = self._load_reader()

    def _load_model(self, model_uri: str) -> Any:
        model_path = require_local_model(model_uri)
        try:
            torch = import_module("torch")
            yolo_class = getattr(import_module("ultralytics"), "YOLO")  # noqa: B009
        except ModuleNotFoundError as error:
            raise ModelLoadError("Dependências de inferência não estão instaladas.") from error

        if self.device.startswith("cuda") and not torch.cuda.is_available():
            raise ModelLoadError("CUDA foi solicitada, mas não está disponível neste ambiente.")

        return yolo_class(model_path).to(self.device)

    def _load_reader(self) -> Any:
        try:
            easyocr = import_module("easyocr")
        except ModuleNotFoundError as error:
            raise ModelLoadError("EasyOCR não está instalado neste ambiente.") from error
        return easyocr.Reader(["en", "pt"], gpu=self.device.startswith("cuda"))

    def detect(self, image: np.ndarray) -> DetectionResult:
        results = self._model.predict(image, conf=self.confidence, device=self.device)
        is_generico = self._contains_generic(results)
        extracted: dict[str, str] = {}

        for item in results:
            if item.boxes is None:
                continue
            for box in item.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                label_name = self._model.names[int(box.cls[0].cpu().item())]
                if label_name == "generico":
                    continue
                text = self._extract_text(image, x1, y1, x2, y2, label_name)
                if text:
                    extracted[label_name] = text

        if is_generico:
            extracted["nome"] = "Medicamento Genérico"

        return DetectionResult(
            is_generico=is_generico,
            data=ExtractedMedicineData(**extracted),
        )

    def _contains_generic(self, results: Any) -> bool:
        for item in results:
            if item.boxes is None or len(item.boxes) == 0:
                continue
            classes = item.boxes.cls.cpu().tolist()
            if any(self._model.names[int(class_id)] == "generico" for class_id in classes):
                return True
        return False

    def _extract_text(
        self, image: np.ndarray, x1: int, y1: int, x2: int, y2: int, label_name: str
    ) -> str:
        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return ""
        result = self._reader.readtext(roi, detail=0, paragraph=False)
        return sanitizar_texto(" ".join(result).strip(), label_name) if result else ""
