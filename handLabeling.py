from pathlib import Path
import csv 

# 12 - "1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16"
# 342 357 - "1, 2, 4, 5, 6, 8" 
# 04-01-010-02-01-04/08/12.svg Foram criados por mim

hand_fills = ['Front White', 'Front Half', 'Front Black', 'Top White', 'Top Half', 'Top Black']
csv_info = []
class_map = []
output_file = Path("class_map")
input_folder = Path("signs/png")
sorted_folder = sorted(input_folder.rglob("*.png"))

last_id = 1529 #1529
temp_sort_H = sorted_folder[:last_id]
temp_sort_O = [] #sorted_folder[last_id:]
with open("help.csv", "r", newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        csv_info.append({"name": row[1], "fill": row[6], "rot": row[7]})

# 0 - square 1 7 9-13 / 1 3-27 29-30 / 1 3-38 / 7 / / 1 6-9 11-14 18-21 23 25-27 / 1 6 8-13 17-22 / 1 11 13 15-19 / 1 16 18-28 30-40 / 1
# 1 - circle 2 8 14 / 2 28 / 2 / 8 / 43 / 2 15 28 / 2 7 14 / 2 14 / 2 9 /
# 2 - oval rectangle 3 / / / / 34 36 38 40 / / / 7 / 4 / 
# 3 - claw / / / / 8-11 / / / / /
# 4 - rectangle 4-6 / / / 3 6 / 2 4 6 12-14 17 19 27-33 35 37 39 44-51 53 55-58 / 3-5 10 16-17 22 24 29-30 / 3-5 15 16 / 4-6 8-10 12 / 5-8 10- 15 17 29 /3-15
# 5 - palm / / / 1-2 4 / / / / / /
# 6 - palm peace / / / 5 / / / / / /
# 7 - palm peace thin/ / / / 23-25 / / / / /
# 8 - palm thin / / / / 1 3 5 7 15-16 18 20-22 26 / / / / /
# 9 - snail / / / / 41 42 / / / 3 / 3 /
# 10 - diagonal rectangle / / / / 52 54 / / / / / /
# 11 - horizontal rectangle / / / /  / / / / / 2 16 <- definitivamente menor


pf_1 = [0, 1, 2, 4, 4, 4, 0, 1, 0, 0, 0, 0, 0, 1]
pf_2 = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
pf_3 = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pf_4 = [5, 5, 4, 5, 6, 4, 0, 4]
pf_5 = [8, 4, 8, 4, 8, 4, 8, 3, 3, 3, 3, 4, 4, 4, 8, 8, 4, 8, 4, 8, 8, 8, 7, 7, 7, 8, 4, 4, 4, 4, 4, 4, 4, 2, 4, 2, 4, 2, 4, 2, 9, 9, 1, 4, 4, 4, 4, 4, 4, 4, 4, 10, 4, 10, 4, 4, 4, 4]
pf_6 = [0, 1, 4, 4, 4, 0, 0, 0, 0, 4, 0, 0, 0, 0, 1, 4, 4, 0, 0, 0, 0, 4, 0, 4, 0, 0, 0, 1, 4, 4]
pf_7 = [0, 1, 4, 4, 4, 0, 1, 0, 0, 0, 0, 0, 0, 1, 4, 4, 0, 0, 0, 0, 0, 0]
pf_8 = [0, 1, 9, 4, 4, 4, 2, 4, 4, 4, 0, 4, 0, 1, 0, 0, 0, 0, 0]
pf_9 = [0, 1, 9, 2, 4, 4, 4, 4, 1, 4, 4, 4, 4, 4, 4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pf_10 = [0, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11]

palm_formats = [pf_1, pf_2, pf_3, pf_4, pf_5, pf_6, pf_7, pf_8, pf_9, pf_10]

#HANDS
hand_fill = 0
csv_id = 0
class_id = 0
for file in temp_sort_H:
    fill = csv_info[csv_id]["fill"]
    rot = csv_info[csv_id]["rot"]
    class_name = csv_info[csv_id]["name"].replace(',', '')
    class_name_add = f"Fill_{hand_fills[hand_fill]}" if int(csv_info[csv_id]["fill"]) > 4 else f"Rot_{hand_fill}"
    a, b, c, d, e = file.stem.split("-")
    main_group_id = int(b)-1
    sec_group_id = int(c)-1
    fill_id = int(e)-1
    palm_format = palm_formats[main_group_id][sec_group_id]

    class_map.append(
        f"{class_id}, {main_group_id}, {sec_group_id}, {fill_id}, \"{class_name} {class_name_add}\", {fill}, {rot}, {file} {palm_format}"
    )
    hand_fill += 1
    class_id += 1 
    if(hand_fill == int(csv_info[csv_id]["fill"]) or csv_info[csv_id]["fill"] == '2'):
        csv_id += 1
        hand_fill = 0

with open(output_file, "w") as f:
    for item in class_map:
        f.write(f"{item}\n")