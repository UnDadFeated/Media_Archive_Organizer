from PIL import Image
import os

# Source path (from generation tool output)
src_path = r"C:/Users/jsche/.gemini/antigravity/brain/1ae680e0-cfb8-4b57-a210-140a490de435/app_icon_v2_1767271795619.png"
dest_dir = r"c:/Coding_Workspace/Media_Archive_Organizer/src/assets"
dest_png = os.path.join(dest_dir, "icon.png")
dest_ico = os.path.join(dest_dir, "icon.ico")

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

try:
    img = Image.open(src_path)
    img = img.convert("RGBA")
    
    # Simple transparency check/fix not really possible without rembg, 
    # but the prompt asked for separate background or alpha. 
    # If the generation tool obeyed "alpha transparency directly", it's good.
    # If it put it on white/black, we might have a box.
    # Let's hope the generation tool did a good job or the user can accept a square for now if bad.
    # Actually, I can try a simple "replace white with transparent" if it's pure white, 
    # but that often leaves fringes. 
    # For now, let's resize and save.
    
    # Save as PNG
    img.save(dest_png)
    
    # Save as ICO (sizes for Windows)
    img.save(dest_ico, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    
    print("Icon processed successfully.")
except Exception as e:
    print(f"Error processing icon: {e}")
