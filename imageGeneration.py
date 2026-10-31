from pathlib import Path
from PIL import Image
import random
import csv
import time

#https://docs.ultralytics.com/datasets/

#symbol = symbol.rotate(rotation)
#rotation = random.choice([0, 45, 90, 135, 180, 225, 270, 315])
def imgGenYolo(folder, symbol_range, max_symbols_per_img, img_per_symbol, img_size):
    input_folder = Path("signs/png")
    output_imgs = "datasetYolo/images/" + folder
    output_labels  = "datasetYolo/labels/" + folder
    sorted_folder = sorted(input_folder.rglob("*.png"))

    class_map = []
    with open("Files/class_map", "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            class_map.append(row[1])

    int_name = 0
    start_time = time.perf_counter()
    for i in range(0, symbol_range+1):
        for j in range(img_per_symbol):
            canvas = Image.new(
                "RGBA",
                (img_size, img_size),
                (255,255,255,255)
            )
            yolo_boxes = []
            placed_boxes = []

            rand_sign = i
            symbol = Image.open(sorted_folder[rand_sign]).convert("RGBA")
            w, h = symbol.size
            scale = random.uniform(0.5, 1.0)
            s_w = w*scale
            s_h = h*scale
            x = random.randint(0, int(img_size-s_w))
            y = random.randint(0, int(img_size-s_h))
            symbol = symbol.resize((
                int(s_w),
                int(s_h)
            ))

            canvas.paste(
                symbol,
                (x,y),
                symbol
            )
            
            placed_boxes.append([x,y,x+w,y+h])    
            yolo_boxes.append([class_map[rand_sign], (x+w/2)/img_size, (y+h/2)/img_size, w/img_size, h/img_size])

            for k in range(max_symbols_per_img):
                rand_sign = random.randint(0, symbol_range)
                symbol = Image.open(sorted_folder[rand_sign]).convert("RGBA")

                w, h = symbol.size
                scale = random.uniform(0.5, 1.0)
                x = random.randint(0, int(img_size-s_w))
                y = random.randint(0, int(img_size-s_h))
                found = False
                tries = 0

                while(not found and tries < 5):
                    scale = random.uniform(0.5, 1.0)
                    s_w = w*scale
                    s_h = h*scale

                    x = random.randint(0, int(img_size-s_w))
                    y = random.randint(0, int(img_size-s_h))

                    if not any(intersect(placed, [x,y,x+s_w,y+s_h]) for placed in placed_boxes):
                        found = True
                        symbol = symbol.resize((
                            int(s_w),
                            int(s_h)
                        ))
                    
                    tries += 1

                if not found:
                    continue

                canvas.paste(
                    symbol,
                    (x,y),
                    symbol
                )

                placed_boxes.append([x,y,x+w,y+h])

                yolo_boxes.append([class_map[rand_sign], (x+w/2)/img_size, (y+h/2)/img_size, w/img_size, h/img_size])
                
               
            with open(Path(output_labels + f"/{int_name}" + ".txt"), "w") as f:
                    for item in yolo_boxes:
                        f.write(" ".join(map(str, item)) + "\n")

            canvas.save(Path(output_imgs + f"/{int_name}" + ".png"))
            int_name +=1

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.4f} seconds")

def imgGenAlexNet(folder, symbol_range, img_per_symbol, img_size):
    input_folder = Path("signs/png")
    output_imgs = "datasetAlexNet/images/" + folder
    output_labels  = "datasetAlexNet/images/" + folder
    sorted_folder = sorted(input_folder.rglob("*.png"))

    int_name = 0
    images = []
    for i in range(0, symbol_range+1):
        for j in range(img_per_symbol):
            canvas = Image.new(
                "RGBA",
                (img_size, img_size),
                (255,255,255,255)
            )
            
            sign = i
            symbol = Image.open(sorted_folder[sign]).convert("RGBA")

            x = int(img_size/2) - int(img_size/4) 
            y = 5

            canvas.paste(
                symbol,
                (x,y),
                symbol
            )
            
            images.append([f"{int_name}.png", i])
            canvas.save(Path(output_imgs + f"/{int_name}" + ".png"))
            int_name +=1

    with open(Path(output_labels + "/labels.csv"), "w") as f:
        for item in images:
            f.write(",".join(map(str, item)) + "\n")

def intersect(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    return not (ax2 <= bx1 or
       ax1 >= bx2 or
       ay2 <= by1 or
       ay1 >= by2
       )        

img_size = 70 #640
symbol_range = 407
#imgGenYolo("train", 5, 0, 5, img_size)
#imgGenYolo("val", 5, 0, 2, img_size)
imgGenAlexNet("train", 5, 5, img_size)
imgGenAlexNet("val", 5, 2, img_size)