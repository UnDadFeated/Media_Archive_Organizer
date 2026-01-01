from PIL import Image
import os

# New Source path (v3 from brain)
src_path = r"C:/Users/jsche/.gemini/antigravity/brain/1ae680e0-cfb8-4b57-a210-140a490de435/app_icon_v3_1767272135812.png"
dest_dir = r"c:/Coding_Workspace/Media_Archive_Organizer/src/assets"
dest_png = os.path.join(dest_dir, "icon.png")
dest_ico = os.path.join(dest_dir, "icon.ico")

def process_icon(image_path):
    print(f"Loading {image_path}...")
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    # Threshold for "black" background (since prompt asked for black)
    # We'll use a low threshold to catch pure black and very dark noise
    threshold = 15 
    
    print("Applying transparency (removing black background)...")
    for item in datas:
        # Check if pixel is dark/black
        # item is (r, g, b, a)
        if item[0] <= threshold and item[1] <= threshold and item[2] <= threshold:
            new_data.append((0, 0, 0, 0)) # Transparent
        else:
            new_data.append(item)

    img.putdata(new_data)
    
    # Auto-Crop to remove empty space (solver for "icon looks small")
    print("Cropping to content bounds...")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        print(f"Cropped to {bbox}")
    
    # Resize to standard icon square (256x256) with padding if needed to keep aspect ratio?
    # Or just max dimension 256. Windows icons are square.
    # Let's resize canvas to 256x256 and center the image.
    
    target_size = (256, 256)
    final_img = Image.new("RGBA", target_size, (0, 0, 0, 0))
    
    # Calculate scale to fit within 256x256
    w, h = img.size
    ratio = min(target_size[0]/w, target_size[1]/h)
    new_w = int(w * ratio)
    new_h = int(h * ratio)
    
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Center paste
    offset = ((target_size[0] - new_w) // 2, (target_size[1] - new_h) // 2)
    final_img.paste(img_resized, offset)
    
    return final_img

try:
    if not os.path.exists(src_path):
        print(f"Error: Source file not found: {src_path}")
        exit(1)

    final_icon = process_icon(src_path)

    # Save as PNG
    final_icon.save(dest_png, "PNG")
    print(f"Saved PNG to {dest_png}")
    
    # Save as ICO (sizes for Windows)
    final_icon.save(dest_ico, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Saved ICO to {dest_ico}")
    
    print("Icon v3 processed successfully.")
    
except Exception as e:
    print(f"Error processing icon: {e}")
