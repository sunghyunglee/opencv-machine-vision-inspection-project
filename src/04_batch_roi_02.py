from pathlib import Path

import cv2


input_dir = Path("samples")
output_dir = Path("outputs/roi")
output_dir.mkdir(parents=True, exist_ok=True)

# 자신의 이미지에 맞게 수정합니다.
roi_table = {
    "20261026_sb.jpg":  (1150, 1480, 2000, 2420),
    "20261026_sb2.jpg": (450, 800, 2580, 3120),
}

extensions = ("20261026_sb*.jpg",)

image_files = []
for pattern in extensions:
    image_files.extend(input_dir.glob(pattern))

image_files = sorted(image_files)

print("전체 이미지 수:", len(image_files))

if not image_files:
    raise RuntimeError(
        "samples 폴더에 jpg/jpeg/png 이미지가 없습니다."
    )

success_count = 0

for image_path in image_files:
    image = cv2.imread(str(image_path))

    if image is None:
        print("읽기 실패:", image_path.name)
        continue

    x1, y1, x2, y2 = roi_table[image_path.name]    

    height, width = image.shape[:2]

    cx1 = max(0, min(x1, width))
    cx2 = max(0, min(x2, width))
    cy1 = max(0, min(y1, height))
    cy2 = max(0, min(y2, height))

    if cx1 >= cx2 or cy1 >= cy2:
        print("ROI 실패:", image_path.name)
        continue

    roi = image[cy1:cy2, cx1:cx2]

    roi_path = output_dir / f"{image_path.stem}_roi_02.jpg"
    preview_path = output_dir / f"{image_path.stem}_preview_02.jpg"

    cv2.imwrite(str(roi_path), roi)

    preview = image.copy()
    cv2.rectangle(
        preview,
        (cx1, cy1),
        (cx2, cy2),
        (0, 255, 0),
        3,
    )
    cv2.imwrite(str(preview_path), preview)

    success_count += 1
    print(image_path.name, "→", roi_path.name)

print("처리 완료:", success_count, "/", len(image_files))
