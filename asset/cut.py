import os
from PIL import Image

# Mở hình ảnh
input_path = "level1.jpg"
img = Image.open(input_path)
width, height = img.size

# 1. Xác định kích thước một ô (cell)
# Chiều rộng 1 ô = Tổng chiều rộng / 10
cell_width = width // 10
# Chiều cao 1 ô = (Chiều rộng 1 ô) * 7/5
cell_height = int(cell_width * 7 / 5)

target_width = 100
target_height = int(target_width * 7 / 5) # = 140

# 2. Tạo thư mục đầu ra
output_dir = "level1/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 3. Tiến hành cắt
cols = 10
rows = height // cell_height

count = 0
for r in range(rows):
    for c in range(cols):
        # Tính toán tọa độ (trái, trên, phải, dưới)
        left = c * cell_width
        top = r * cell_height
        right = left + cell_width
        bottom = top + cell_height
        
        # Kiểm tra nếu vùng cắt vượt quá chiều cao ảnh gốc thì dừng hoặc cắt sát biên
        if bottom > height:
            continue
            
        # Cắt và lưu
        card = img.crop((left, top, right, bottom))
        card.save(os.path.join(output_dir, f"card_{r}_{c}.jpg"))
        count += 1

left = width - 500
top = height - 700
right = width
bottom = height
card = img.crop((left, top, right, bottom))
card.save(os.path.join(output_dir, f"card_4_0.jpg"))

print(f"Đã cắt xong {count} hình vào thư mục '{output_dir}'")