from pathlib import Path
import csv

class_map = []
names = [Index, Index Middle, Index Middle Thumb]
with open("Files/class_map", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        name = row[2].replace('"', '')
        class_map.append(name)

with open("dataset/data.yaml", "w") as f:
    f.write("path: ./dataset\n")
    f.write("train: images/train\n")
    f.write("val: images/val\n")
    f.write("\nnames:\n")

    for i, name in enumerate(names):
        name = name.replace("\xa0", " ").strip()
        f.write(f"  {i}: {name}\n")