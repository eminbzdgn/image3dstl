# -----------------------------
# KÜTÜPHANELER
# -----------------------------
from PIL import Image
import numpy as np
from stl import mesh

# -----------------------------
# KULLANICI AYARLARI (SİTEDEKİ GİBİ)
# -----------------------------
IMAGE_PATH = "aaaa.png"
OUTPUT_STL = "resim2.stl"

MAX_SIZE_MM = 180          # Maximum Size (MM) → BORDER DAHİL
BORDER_MM = 10             # Kenarlık
PX_PER_MM = 10             # Vectors per Pixel (kalite)

MIN_THICKNESS = 0.6        # Thinnest Layer
MAX_THICKNESS = 1.5        # Thickness

# -----------------------------
# OTOMATİK TÜREVLER
# -----------------------------
PIXEL_SCALE = 1 / PX_PER_MM

IMAGE_MAX_MM = MAX_SIZE_MM - 2 * BORDER_MM
if IMAGE_MAX_MM <= 0:
    raise ValueError("Border çok büyük, görüntüye yer kalmadı")

# -----------------------------
# RESMİ OKU
# -----------------------------
img = Image.open(IMAGE_PATH).convert("L")

orig_w, orig_h = img.size

# Uzun kenarı bul
if orig_w >= orig_h:
    target_w_mm = IMAGE_MAX_MM
    target_h_mm = IMAGE_MAX_MM * (orig_h / orig_w)
else:
    target_h_mm = IMAGE_MAX_MM
    target_w_mm = IMAGE_MAX_MM * (orig_w / orig_h)

# MM → PX
target_w_px = int(target_w_mm * PX_PER_MM)
target_h_px = int(target_h_mm * PX_PER_MM)

# Resize
img = img.resize((target_w_px, target_h_px), Image.LANCZOS)

pixels = np.array(img)
height, width = pixels.shape

# -----------------------------
# KALINLIK HARİTASI
# -----------------------------
depth = MAX_THICKNESS - MIN_THICKNESS
z_map = MAX_THICKNESS - (pixels / 255.0) * depth

# -----------------------------
# MESH OLUŞTURMA
# -----------------------------
triangles = []

def tri(a, b, c):
    triangles.append([a, b, c])

# Görüntünün başlangıç offset'i (border)
offset_x = BORDER_MM
offset_y = BORDER_MM

# -----------------------------
# ÜST YÜZEY (GÖRÜNTÜ)
# -----------------------------
for y in range(height - 1):
    for x in range(width - 1):
        p1 = [offset_x + x * PIXEL_SCALE,     offset_y + y * PIXEL_SCALE,     z_map[y][x]]
        p2 = [offset_x + (x+1) * PIXEL_SCALE, offset_y + y * PIXEL_SCALE,     z_map[y][x+1]]
        p3 = [offset_x + (x+1) * PIXEL_SCALE, offset_y + (y+1) * PIXEL_SCALE, z_map[y+1][x+1]]
        p4 = [offset_x + x * PIXEL_SCALE,     offset_y + (y+1) * PIXEL_SCALE, z_map[y+1][x]]

        tri(p1, p2, p3)
        tri(p3, p4, p1)

# -----------------------------
# ALT TABAN (BORDER + GÖRÜNTÜ)
# -----------------------------
total_px = int(MAX_SIZE_MM * PX_PER_MM)

for y in range(total_px - 1):
    for x in range(total_px - 1):
        p1 = [x * PIXEL_SCALE,     y * PIXEL_SCALE,     0]
        p2 = [(x+1) * PIXEL_SCALE, y * PIXEL_SCALE,     0]
        p3 = [(x+1) * PIXEL_SCALE, (y+1) * PIXEL_SCALE, 0]
        p4 = [x * PIXEL_SCALE,     (y+1) * PIXEL_SCALE, 0]

        tri(p3, p2, p1)
        tri(p1, p4, p3)

# -----------------------------
# STL YAZ
# -----------------------------
model = mesh.Mesh(np.zeros(len(triangles), dtype=mesh.Mesh.dtype))
for i, t in enumerate(triangles):
    model.vectors[i] = t

model.save(OUTPUT_STL)

# -----------------------------
# BİLGİ
# -----------------------------
print("STL hazır:", OUTPUT_STL)
print("Toplam ölçü (mm):", MAX_SIZE_MM)
print("Görüntü alanı (mm):", round(target_w_mm,1), "x", round(target_h_mm,1))
print("Border (mm):", BORDER_MM)
print("Kalite (px/mm):", PX_PER_MM)
