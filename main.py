# -----------------------------
# GEREKLİ KÜTÜPHANELER
# -----------------------------
from PIL import Image              # Resmi açmak için
import numpy as np                 # Matematik ve array işlemleri
from stl import mesh               # STL dosyası üretmek için

# -----------------------------
# AYARLAR (BURASI SENİN OYUN ALANIN)
# -----------------------------
IMAGE_PATH = "aaa.png"            # Kullanacağın resim
OUTPUT_STL = "lithophane.stl"

PIXEL_SCALE = 0.2                  # 1 piksel kaç mm olsun (X,Y)
MIN_THICKNESS = 0.8                # En ince yer (mm)
MAX_THICKNESS = 3.0                # En kalın yer (mm)

# -----------------------------
# RESMİ OKU VE GRAYSCALE YAP
# -----------------------------
img = Image.open(IMAGE_PATH)
img = img.convert("L")             # L = grayscale

# Resmi numpy array'e çevir
pixels = np.array(img)

height, width = pixels.shape

# -----------------------------
# PIKSEL -> KALINLIK HESABI
# -----------------------------
depth = MAX_THICKNESS - MIN_THICKNESS

# Her piksel için Z değerini hesapla
z_map = MAX_THICKNESS - (pixels / 255.0) * depth

# -----------------------------
# MESH OLUŞTURMA
# -----------------------------
triangles = []

def add_triangle(p1, p2, p3):
    triangles.append([p1, p2, p3])

# ÜST YÜZEY
for y in range(height - 1):
    for x in range(width - 1):
        # 4 köşe noktası
        p1 = [x * PIXEL_SCALE,     y * PIXEL_SCALE,     z_map[y][x]]
        p2 = [(x+1) * PIXEL_SCALE, y * PIXEL_SCALE,     z_map[y][x+1]]
        p3 = [(x+1) * PIXEL_SCALE, (y+1) * PIXEL_SCALE, z_map[y+1][x+1]]
        p4 = [x * PIXEL_SCALE,     (y+1) * PIXEL_SCALE, z_map[y+1][x]]

        # Quad -> 2 üçgen
        add_triangle(p1, p2, p3)
        add_triangle(p3, p4, p1)

# -----------------------------
# ALT TABAN (DÜZ)
# -----------------------------
for y in range(height - 1):
    for x in range(width - 1):
        p1 = [x * PIXEL_SCALE,     y * PIXEL_SCALE,     0]
        p2 = [(x+1) * PIXEL_SCALE, y * PIXEL_SCALE,     0]
        p3 = [(x+1) * PIXEL_SCALE, (y+1) * PIXEL_SCALE, 0]
        p4 = [x * PIXEL_SCALE,     (y+1) * PIXEL_SCALE, 0]

        add_triangle(p3, p2, p1)
        add_triangle(p1, p4, p3)

# -----------------------------
# STL YAZMA
# -----------------------------
litho_mesh = mesh.Mesh(np.zeros(len(triangles), dtype=mesh.Mesh.dtype))

for i, tri in enumerate(triangles):
    litho_mesh.vectors[i] = tri

litho_mesh.save(OUTPUT_STL)

print("STL oluşturuldu:", OUTPUT_STL)
