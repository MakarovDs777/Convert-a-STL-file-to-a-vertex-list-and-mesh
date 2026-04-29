import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
import struct

def parse_binary_stl(filepath):
    """Парсинг бинарного STL файла"""
    vertices = []
    faces = []
    
    with open(filepath, 'rb') as f:
        # Пропускаем 80-байтовый заголовок
        f.read(80)
        # Количество треугольников (4 байта, little-endian)
        num_triangles = struct.unpack('<I', f.read(4))[0]
        
        for i in range(num_triangles):
            # Нормаль (3 float по 4 байта) — пропускаем
            f.read(12)
            # 3 вершины (каждая: 3 float по 4 байта)
            for _ in range(3):
                x, y, z = struct.unpack('<fff', f.read(12))
                vertices.append([x, y, z])
            # Атрибут (2 байта) — пропускаем
            f.read(2)
            # Грань: индексы трёх вершин
            base_idx = i * 3
            faces.append([base_idx, base_idx + 1, base_idx + 2])
    
    return vertices, faces

def parse_ascii_stl(filepath):
    """Парсинг текстового (ASCII) STL файла"""
    vertices = []
    faces = []
    vertex_count = 0
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('facet normal'):
            # Начало грани — пропускаем нормаль
            pass
        elif line.startswith('vertex'):
            # Читаем 3 вершины подряд
            face_start = len(vertices)
            for _ in range(3):
                parts = lines[i].strip().split()
                if len(parts) >= 4:
                    x, y, z = map(float, parts[1:4])
                    vertices.append([x, y, z])
                i += 1
            faces.append([face_start, face_start + 1, face_start + 2])
            continue
        elif line.startswith('endsolid'):
            break
        
        i += 1
    
    return vertices, faces

def stl_to_text(stl_file):
    """Определяет формат STL и парсит его"""
    with open(stl_file, 'rb') as f:
        header = f.read(80)
    
    # Определяем формат: ASCII начинается с "solid", бинарный — с байтов
    try:
        header_str = header.decode('ascii').strip()
        if header_str.startswith('solid'):
            # Дополнительная проверка: ищем "facet" в следующих строках
            with open(stl_file, 'r') as f:
                for _ in range(5):
                    line = f.readline().strip().lower()
                    if 'facet' in line:
                        return parse_ascii_stl(stl_file)
    except:
        pass
    
    # По умолчанию — бинарный
    return parse_binary_stl(stl_file)

def format_output(vertices, faces):
    """Форматирует вершины и грани в читаемый текст"""
    result = []
    
    result.append("=" * 60)
    result.append("РАЗБОР STL ФАЙЛА")
    result.append("=" * 60)
    
    result.append(f"\n📐 Всего вершин: {len(vertices)}")
    result.append(f"🔷 Всего граней: {len(faces)}")
    
    result.append("\n" + "-" * 60)
    result.append("ВЕРШИНЫ (Vertices):")
    result.append("-" * 60)
    for i, v in enumerate(vertices):
        result.append(f"  v{i:6d}: ({v[0]:10.6f}, {v[1]:10.6f}, {v[2]:10.6f})")
    
    result.append("\n" + "-" * 60)
    result.append("ГРАНИ (Faces) — треугольники:")
    result.append("-" * 60)
    for i, f in enumerate(faces):
        result.append(f"  f{i:6d}: {f[0]:6d} {f[1]:6d} {f[2]:6d}")
    
    result.append("\n" + "=" * 60)
    result.append("ФОРМАТ ДЛЯ ПРОГРАММНОЙ ОБРАБОТКИ:")
    result.append("=" * 60)
    result.append(f"\nVertices: {vertices}")
    result.append(f"\nFaces: {faces}")
    
    return "\n".join(result)

def save_to_file(text):
    """Сохраняет результат на рабочий стол"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "stl_output.txt")
    with open(desktop_path, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"✅ Сохранено в {desktop_path}")

def select_stl_file():
    """Диалог выбора STL файла"""
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Выберите STL файл",
        filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
    )
    
    if file_path:
        print(f"📂 Обрабатываю: {file_path}")
        vertices, faces = stl_to_text(file_path)
        text = format_output(vertices, faces)
        print(text)
        save_to_file(text)
        return vertices, faces
    else:
        print("❌ Файл не выбран.")
        return None, None

# Запуск
if __name__ == "__main__":
    vertices, faces = select_stl_file()
