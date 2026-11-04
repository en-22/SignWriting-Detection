from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
import csv
import time

#https://docs.ultralytics.com/datasets/

STOCK_DIR = Path("stockImages")
_stock_cache = []
_TEXT_CHARS = "abcdefghijklmnopqrstuvwxyzáãéêíóúç" * 2 + "0123456789.,-"


# Open all stock images once and cache them
def _stock_images():
    if not _stock_cache:
        for img in sorted(STOCK_DIR.iterdir()):
            if img.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
                _stock_cache.append(Image.open(img).convert("RGB"))
        if not _stock_cache:
            raise FileNotFoundError(f"No images found in {STOCK_DIR}")
    
    return _stock_cache

def _crop_stock_patch(w, h):
    img = random.choice(_stock_cache)

    if img.width < w or img.height < h: # Enlarge if image is smaller than canvas          
        k = math.ceil(max(w / img.width, h / img.height))
        img = img.resize((img.width * k, img.height * k))
    
    x = random.randint(0, img.width - w)
    y = random.randint(0, img.height - h)
    
    return img.crop((x, y, x + w, y + h))

def _intersect(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    return not (
        ax2 <= bx1 or
        ax1 >= bx2 or
        ay2 <= by1 or
        ay1 >= by2
    )

def _rotate_symbol(symbol, angle):
    rotated = symbol.rotate(
        angle, 
        expand=True, 
        resample=Image.BICUBIC, 
        fillcolor=(0, 0, 0, 0)
    )
    box = rotated.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()   # ignore faint fringe
    return rotated.crop(box) if box else rotated

def _touches(mask, avoid_boxes, gap):
    """True if any non-zero pixel of the mask lies inside an avoid box (padded by gap)."""
    w, h = mask.size
    for x1, y1, x2, y2 in avoid_boxes:
        region = (max(0, x1 - gap), max(0, y1 - gap), min(w, x2 + gap), min(h, y2 + gap))
        if region[2] > region[0] and region[3] > region[1] and mask.crop(region).getbbox():
            return True
    return False

def _scribble(canvas, avoid_boxes, gap=2):
    w, h = canvas.size
    step = max(4, max(w, h) // 2)

    for _ in range(20):
        x, y = random.randint(0, w), random.randint(0, h)
        pts = [(x, y)]
        for _ in range(random.randint(3, 8)):
            x += random.randint(-step, step)
            y += random.randint(-step, step)
            pts.append((x, y))
        mask = Image.new("L", (w, h), 0)                         # the stroke as a white-on-black mask
        ImageDraw.Draw(mask).line(pts, fill=255, width=random.randint(2, 4))

        if not mask.getbbox():                                   # stroke fell completely outside the canvas
            continue

        if not _touches(mask, avoid_boxes, gap):
            canvas.paste((0, 0, 0), (0, 0, w, h), mask)
            return True

    return False

def _random_text():
    words = []
    for _ in range(random.randint(5, 10)):
        word = "".join(random.choices(_TEXT_CHARS, k=random.randint(2, 9)))
        words.append(word.capitalize() if random.random() < 0.3 else word)
    if random.random() < 0.2:
        words.append(str(random.randint(1, 99)))
    return " ".join(words)

def _add_text(canvas, avoid_boxes, gap=2):
    w, h = canvas.size
    font_h = random.randint(5, 28)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        size=font_h
    )
    for _ in range(10):
        text = _random_text()
        mask = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(mask)

        
        width = d.textlength(text, font=font)
        height = font_h  # approximate height for the default font
        left, top, right, bottom = 0, 0, width, height
        tw, th = right - left, bottom - top

        x = random.randint(-tw // 2, w - tw // 2) - left
        y = random.randint(-th // 2, h - th // 2) - top

        d.text((x, y), text, fill=255, font=font)

        if not mask.getbbox():                                   # nothing visible inside the canvas
            continue

        if not _touches(mask, avoid_boxes, gap):
            canvas.paste(tuple((0, 0, 0)), (0, 0, w, h), mask)

def _generateCanvas(w, h):
    bg_color = random.randint(0,2) # 0 = Clear White Bg # 1 = Rand_color Bg
    squares = random.randint(0,2) # 0 = N squares # 1 = Has squares
    stock_photo = random.randint(0,2)

    if bg_color < 2:
        color = (255, 255, 255)
    else:
        color = tuple(random.randint(180, 255) for _ in range(3))

    canvas = Image.new(
        "RGB",
        (w, h),
        color
    )

    if squares == 2:
        for _ in range(random.randint(0, 4)):
            
            rect_w = random.randint(w // 2, w)
            rect_h = random.randint(h // 2, h)

            pos_x = random.randint(0, w - rect_w)
            pos_y = random.randint(0, h - rect_h)

            rand_color = tuple(random.randint(50, 255) for _ in range(3))

            canvas.paste(
                rand_color,
                (pos_x, pos_y, pos_x + rect_w, pos_y + rect_h)
            )

    if stock_photo < 2:
        return canvas
    return Image.blend(canvas, _crop_stock_patch(w, h), 0.3)
    
def _recolor_symbol(symbol):
    new_color = tuple(random.randint(0, 150) for _ in range(3))

    pixels = symbol.load()

    for y in range(symbol.height):
        for x in range(symbol.width):
            r, g, b, a = pixels[x, y]

            if a > 0 and r < 50 and g < 50 and b < 50:
                pixels[x, y] = (*new_color, a)
    return symbol

def imgGenYolo(folder, symbol_range, max_symbols_per_img, img_per_symbol, img_size):
    _stock_images()

    input_folder = Path("signs/png")
    output_imgs = Path("datasetYolo/images/" + folder)

    output_labels = Path("datasetYolo/labels/" + folder)
    output_imgs.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    sorted_folder = sorted(input_folder.rglob("*.png"))

    # class_map = []
    # with open("Files/class_map", "r", newline="") as file:
    #     reader = csv.reader(file)
    #     for row in reader:
    #         class_map.append({
    #             "id": int(row[0]),
    #             "main_class": int(row[1]), 
    #             "sec_class": int(row[2]), 
    #             "fill": int(row[3]), 
    #             "max_fills": int(row[5])
    #         })

    int_name = 0

    for i in range(0, symbol_range):
        for j in range(img_per_symbol):
            canvas = _generateCanvas(img_size,img_size)

            yolo_labels = []
            placed_boxes = []

            symbol = Image.open(sorted_folder[i]).convert("RGBA")
            scale = random.uniform(0.5, 1.0)
            temp_symbol = symbol.resize((int(symbol.width * scale), int(symbol.height * scale)))
            
            rand_rot = random.randint(0,7)

            if rand_rot:
                temp_symbol = _rotate_symbol(temp_symbol, 45 * rand_rot)

            h = temp_symbol.height
            w = temp_symbol.width

            if w >= img_size or h >= img_size:
                continue

            x = random.randint(0, img_size-temp_symbol.width)
            y = random.randint(0, img_size-temp_symbol.height)

            canvas.paste(
                temp_symbol,
                (x,y),
                temp_symbol
            )
            
            placed_boxes.append([x,y,x+w,y+h])    
            yolo_labels.append([0, (x+w/2)/img_size, (y+h/2)/img_size, w/img_size, h/img_size])

            for _ in range(max_symbols_per_img):
                rand_sign = random.randint(0, symbol_range-1)
                symbol = Image.open(sorted_folder[rand_sign]).convert("RGBA")

                scale = random.uniform(0.5, 1.0)
                temp_symbol = symbol.resize((int(symbol.width * scale), int(symbol.height * scale)))

                rand_rot = random.randint(0,7)

                if rand_rot:
                    temp_symbol = _rotate_symbol(temp_symbol, 45 * rand_rot)
                
                h = temp_symbol.height
                w = temp_symbol.width

                if w >= img_size or h >= img_size:
                    continue

                found = False
                tries = 0

                while(not found and tries < 5):

                    x = random.randint(0, int(img_size-w))
                    y = random.randint(0, int(img_size-h))

                    if not any(_intersect(placed, [x,y,x+w,y+h]) for placed in placed_boxes):
                        found = True
                        
                    tries += 1

                if not found:
                    continue

                if random.randint(0,1):
                    temp_symbol = _recolor_symbol(temp_symbol)

                canvas.paste(
                    temp_symbol,
                    (x,y),
                    temp_symbol
                )

                placed_boxes.append([x,y,x+w,y+h])

                yolo_labels.append([0, (x+w/2)/img_size, (y+h/2)/img_size, w/img_size, h/img_size])
                
            
            with open(output_labels / f"{int_name}.txt", "w") as f:
                    for item in yolo_labels:
                        f.write(" ".join(map(str, item)) + "\n")

            _scribble(canvas, placed_boxes)
            _add_text(canvas, placed_boxes)          
            canvas.save(output_imgs / f"{int_name}.png")
            int_name +=1

def imgGenAlexNet(folder, symbol_range, rot_alternatives = 0, margin_frac=0.15):
    if not 0 <= rot_alternatives <= 7:
        rot_alternatives = 0
    
    input_folder = Path("signs/png")
    output_path = Path("datasetAlexNet/images/" + folder)
    output_path.mkdir(parents=True, exist_ok=True)
    sorted_folder = sorted(input_folder.rglob("*.png"))

    #sec_classes_per_main = [14, 16, 38, 8, 58, 30, 22, 19, 40, 16]
    sec_class_sum_per_main = [0, 14, 30, 68, 76, 134, 164, 186, 205, 245]

    label_types = [
        "rot_labels", #45, 90, 135, 180, 225, 270, 315
        "fill_labels", #W, H, B
        "view_labels", #F, T
        "all_fills_labels",  #FW, FH, FB, TW, TH, TB
        "main_class_labels",  #0 ... 9
        "main_class_labels_no_rot",  #0 ... 9
        "sec_class_labels",  # 0 ... 13, ..., 0 ... 15
        "all_class_labels",  # 0 ... 260
    ]

    labels = {label: [] for label in label_types}

    class_map = []
    with open("Files/class_map", "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            class_map.append({
                "id": int(row[0]),
                "main_class": int(row[1]), 
                "sec_class": int(row[2]), 
                "fill": int(row[3]), 
                "max_fills": int(row[5])
            })

    int_name = 0

    for i in range(0, symbol_range+1):
        symbol = Image.open(sorted_folder[i]).convert("RGBA")
        fill = class_map[i]["fill"]
        main_class = class_map[i]["main_class"]
        sec_class = class_map[i]["sec_class"]

        rotations = [0] + random.sample(range(1, 8), rot_alternatives)
        
        for rot_count in rotations:
            img_name = f"{int_name}.png"

            scale = random.uniform(0.5, 1.0)
            temp_symbol = symbol.resize((int(symbol.width * scale), int(symbol.height * scale)))

            if rot_count:
                temp_symbol = _rotate_symbol(temp_symbol, 45 * rot_count)

            mmax = int(max(temp_symbol.size) * margin_frac)
            mmin = int(min(temp_symbol.size) * margin_frac)

            h_margin = 2*random.randint(mmin, mmax)
            v_margin = 2*random.randint(mmin, mmax)

            canvas = _generateCanvas(temp_symbol.width+h_margin, temp_symbol.height+v_margin)

            canvas.paste(
                temp_symbol,
                (random.randint(0, h_margin), random.randint(0, v_margin)),
                temp_symbol
            )

            labels["rot_labels"].append([img_name, rot_count])
            labels["main_class_labels"].append([img_name, main_class])

            if rot_count == 0:
                labels["fill_labels"].append([img_name, fill % 3])
                labels["view_labels"].append([img_name, fill // 3])
                labels["all_fills_labels"].append([img_name, fill])
                labels["main_class_labels_no_rot"].append([img_name, main_class])
                labels["sec_class_labels"].append([img_name, sec_class])
                labels["all_class_labels"].append([img_name, sec_class_sum_per_main[main_class] + sec_class])
               
             
            canvas.save(output_path / img_name)
            int_name+=1
            
    for label in label_types:
        with open(output_path / f"{label}.csv", "w") as f:
            for item in labels[label]:
                f.write(",".join(map(str, item)) + "\n")
        

imgGenYolo("train", 5, 3, 1, 640)