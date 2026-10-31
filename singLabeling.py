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

last_id = 408 #1529
temp_sort_H = sorted_folder[:last_id]
temp_sort_O = [] #sorted_folder[last_id:]
with open("help.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        csv_info.append({"name": row[1], "fill": row[6], "rot": row[7]})


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
        f"{class_id}, {int(b)-1}, \"{class_name} {class_name_add}\", {fill}, {rot}, {file}"
    )
    hand_fill += 1
    class_id += 1 
    if(hand_fill == int(csv_info[csv_id]["fill"]) or csv_info[csv_id]["fill"] == '2'):
        csv_id += 1
        hand_fill = 0


fill_count = 0
rot_count = 0
for file in temp_sort_O:
    fill = csv_info[csv_id]["fill"]
    rot = csv_info[csv_id]["rot"] 
    class_name = csv_info[csv_id]["name"]
    class_map.append(
        f"{class_id}, {file.stem}, \"{class_name} Fill_{fill_count} Rot_{rot_count}\", {fill}, {rot}, {file}" 
    )
    
    class_id += 1
    if(csv_id + 1 in odds):
        fill_count += 1
    else:
        rot_count += 1
        if(rot_count == int(csv_info[csv_id]["rot"])):
            rot_count = 0
            fill_count += 1

    if(fill_count == int(csv_info[csv_id]["fill"])):
        csv_id += 1
        fill_count = 0
        rot_count = 0


with open(output_file, "w") as f:
    for item in class_map:
        f.write(f"{item}\n")
