from pathlib import Path
import csv 

# 12 - "1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16"
# 342 357 - "1, 2, 4, 5, 6, 8" 
# 04-01-010-02-01-04/08/12.svg Foram criados por mim

hand_fills = ['Front White', 'Front Half', 'Front Black', 'Top White', 'Top Half', 'Top Black']
odds = [277, 283, 422, 483, 484, 485, 486, 487, 494, 495, 639, 640, 641, 650, 651, 652] + list(range(288, 334+1))  + list(range(338, 385+1)) + list(range(392, 418+1)) + list(range(502, 511+1))
csv_info = []
class_map = []
output_file = Path("Files/class_map")
input_folder = Path("signs/png")
sorted_folder = sorted(input_folder.rglob("*.png"))

last_id = 1529 #1529
temp_sort_H = sorted_folder[:last_id]
temp_sort_O = [] #sorted_folder[last_id:]
with open("help.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        csv_info.append({"name": row[1], "fill": row[6], "rot": row[7]})

# s 1 7 9-13 / 1 3-27 29-30 / 1 3-38 / 7 / / 1 6-9 11-14 18-21 23 25-27 / 1 6 8-13 17-22 / 1 11 13 15-19 / 1 16 18-28 30-40 / 1
# c 2 8 14 / 2 28 / 2 / 8 / 43 / 2 15 28 / 2 7 14 / 2 14 / 2 9 /
# or 3 / / / / 34 36 38 40 / / / 7 / 4 / 
# ort / / / / 8-11 / / / / /
# sr / / / / 2 4 6 17 19 / / / / / 2 16
# r 4-6 / / / 3 6 / 12-14 27-33 35 37 39 44-51 53 55-58 / 3-5 10 16-17 22 24 29-30 / 3-5 15 16 / 4-6 8-10 12 / 5-8 10- 15 17 29 /3-15
# p / / / 1-2 4 / / / / / /
# v / / / 5 / / / / / /
# vt / / / / 23-25 / / / / /
# pf / / / / 1 3 5 7 15-16 18 20-22 26 / / / / /
# s / / / / 41 42 / / / 3 / 3 /
# nseitorto / / / / 52 54 / / / / / /
# HANDS
hand_fill = 0
csv_id = 0
class_id = 0
for file in temp_sort_H:
    fill = csv_info[csv_id]["fill"]
    rot = csv_info[csv_id]["rot"]
    class_name = csv_info[csv_id]["name"].replace(',', '')
    class_name_add = f"Fill_{hand_fills[hand_fill]}" if int(csv_info[csv_id]["fill"]) > 4 else f"Rot_{hand_fill}"
    a, b, c, d, e = file.stem.split("-")
    class_map.append(
        f"{class_id}, {int(b)-1}, {int(c)-1}, {int(e)-1}, \"{class_name} {class_name_add}\", {fill}, {rot}, {file}"
    )
    hand_fill += 1
    class_id += 1 
    if(hand_fill == int(csv_info[csv_id]["fill"]) or csv_info[csv_id]["fill"] == '2'):
        csv_id += 1
        hand_fill = 0
