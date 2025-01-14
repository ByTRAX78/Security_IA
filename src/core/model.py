import supervision as sv
from inference import get_model


class YOLOModel:
    def __init__(self, model_id: str = "weapons_v2_adrian/9"):
        print("🔄 Cargando modelo...")
        self.model = get_model(model_id=model_id)
        self.class_names = {0: "Sospechoso", 1: "guns", 2: "risk_woman"}
        print("✅ Modelo cargado exitosamente")

    def predict(self, frame):
        results = self.model.infer(frame)[0]
        return sv.Detections.from_inference(results)

    def get_class_name(self, class_id: int) -> str:
        return self.class_names.get(class_id, "Unknown")


def load_model():
    return YOLOModel()
