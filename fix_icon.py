from PIL import Image
import os

# Paths
src_dir = r"c:/Coding_Workspace/Media_Archive_Organizer/src/assets"
src_png = os.path.join(src_dir, "icon.png") # The one we saved previously
dest_ico = os.path.join(src_dir, "icon.ico")

def make_transparent(image_path):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    # Threshold for "white"
    threshold = 240 
    
    for item in datas:
        # Check if pixel is close to white
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0)) # Fully transparent
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

try:
    print(f"Processing {src_png}...")
    
    # Reload the original generated image if possible to avoid degradation, 
    # but strictly speaking `icon.png` is what we have unless we go back to the brain path.
    # Let's use the brain path one if I can remember it? 
    # v2 generation path: C:/Users/jsche/.gemini/antigravity/brain/1ae680e0-cfb8-4b57-a210-140a490de435/app_icon_v2_1767271795619.png
    original_brain_path = r"C:/Users/jsche/.gemini/antigravity/brain/1ae680e0-cfb8-4b57-a210-140a490de435/app_icon_v2_1767271795619.png"
    
    if os.path.exists(original_brain_path):
        print("Using original high-res source from brain...")
        img = make_transparent(original_brain_path)
    else:
        print("Using existing src/assets/icon.png...")
        img = make_transparent(src_png)

    # Save fixed PNG
    img.save(src_png, "PNG")
    
    # Save ICO
    img.save(dest_ico, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    
    print("Icon transparency applied successfully.")
    
except Exception as e:
    print(f"Error fixing icon: {e}")
