from pathlib import Path
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(data="dataset/data.yaml", epochs=50, imgsz=640, batch=64)