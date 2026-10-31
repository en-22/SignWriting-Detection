import argparse
import os

import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms.functional as F
from PIL import Image, ImageDraw
from torchvision import transforms
from ultralytics import YOLO
from alexNetTrain import PadToSquare, preprocess_val
# ------------------------------------------------------------------
# SETTINGS: edit these to match your training
# ------------------------------------------------------------------
YOLO_WEIGHTS = "runs/detect/train/weights/best.pt"
ALEXNET_WEIGHTS = "best_alexnet.pth"                  # saved state_dict from training
NUM_CLASSES = 7                                       # must equal the value used in training

# Index -> name. The order MUST match the integer labels in your labels.csv.
CLASS_NAMES = ["class0", "class1", "class2", "class3", "class4", "class5", "reject"]
REJECT_CLASS = 6          # index of the reject class, or None if you don't have one

YOLO_CONF = 0.25          # minimum YOLO detection confidence (tune on validation)
CLASSIFIER_CONF = 0.70    # minimum AlexNet softmax confidence (tune on validation)

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")

def load_alexnet(device):
    alexnet = models.alexnet(weights=None)
    alexnet.classifier[6] = torch.nn.Linear(
        alexnet.classifier[6].in_features, NUM_CLASSES
    )
    alexnet.load_state_dict(torch.load(ALEXNET_WEIGHTS, map_location=device))
    alexnet.to(device)
    alexnet.eval()   # turns off dropout: required for inference

    return alexnet

def detect_signs(image_path, detector, classifier, device):
    image = Image.open(image_path).convert("RGB")

    # Yolo
    yolo_result = detector.predict(image, conf=YOLO_CONF, verbose=False)[0]
    boxes = yolo_result.boxes.xyxy.cpu().numpy()      # (N, 4): x1, y1, x2, y2 in pixels
    box_scores = yolo_result.boxes.conf.cpu().numpy()  # (N,)

    if len(boxes) == 0:
        return image, []

    # Crop each box and preprocess
    crops, valid_idx = [], []
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(image.width, int(x2)), min(image.height, int(y2))
        
        if x2 - x1 < 2 or y2 - y1 < 2:      # skip degenerate boxes
            continue
        crops.append(preprocess_val(image.crop((x1, y1, x2, y2))))
        valid_idx.append(i)

    if not crops:
        return image, []

    # 3) Classify all crops in one batch
    batch = torch.stack(crops).to(device)
    with torch.no_grad():
        logits = classifier(batch)
        probs = torch.softmax(logits, dim=1)
        confs, preds = probs.max(dim=1)

    # 4) Collect results
    detections = []
    for j, i in enumerate(valid_idx):
        cls = int(preds[j])
        conf = float(confs[j])
        accepted = conf >= CLASSIFIER_CONF and cls != REJECT_CLASS
        detections.append({
            "box": tuple(int(v) for v in boxes[i]),
            "yolo_conf": float(box_scores[i]),
            "class_id": cls,
            "class_name": CLASS_NAMES[cls],
            "class_conf": conf,
            "accepted": accepted,
        })
    return image, detections


# ------------------------------------------------------------------
# Drawing results
# ------------------------------------------------------------------
def draw_detections(image, detections, show_rejected=False):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    for d in detections:
        if not d["accepted"] and not show_rejected:
            continue
        color = (0, 160, 0) if d["accepted"] else (200, 0, 0)
        x1, y1, x2, y2 = d["box"]
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        draw.text((x1, max(0, y1 - 12)),
                  f'{d["class_name"]} {d["class_conf"]:.2f}', fill=color)
    return out


# ------------------------------------------------------------------
# Command line
# ------------------------------------------------------------------
def main():
    out_path = results
    in_path = images
    detector = YOLO(YOLO_WEIGHTS)
    classifier = load_alexnet(device)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    os.makedirs(out_path exist_ok=True)

    if os.path.isdir(in_path):
        files = sorted(
            os.path.join(in_path, f) for f in os.listdir(in_path)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        )
    else:
        files = [in_path]

    for path in files:
        image, detections = detect_signs(path, detector, classifier, device)
        kept = [d for d in detections if d["accepted"]]
        print(f"\n{os.path.basename(path)}: {len(kept)} accepted / {len(detections)} detected")
        for d in kept:
            print(f'  {d["class_name"]:>10}  conf={d["class_conf"]:.2f}  box={d["box"]}')

        annotated = draw_detections(image, detections, args.show_rejected)
        annotated.save(os.path.join(args.out, os.path.basename(path)))


if __name__ == "__main__":
    main()