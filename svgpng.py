import cairosvg
from pathlib import Path

input_folder = Path("signs/svg")
output_folder = Path("signs/png")

for svg_file in input_folder.rglob("*.svg"):
    relative_path = svg_file.relative_to(input_folder)
    output_file = (output_folder / relative_path).with_suffix(".png")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    cairosvg.svg2png(
        url=str(svg_file),
        write_to=str(output_file),
        scale=2
    )

    print(f"Converted {svg_file} -> {output_file}")