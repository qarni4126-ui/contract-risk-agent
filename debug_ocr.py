import pytesseract
from PIL import Image
import os

print("=" * 60)
print("🔍 TESSERACT DEBUG")
print("=" * 60)

# Check 1: Tesseract command
print("\n1️⃣ Checking Tesseract command...")
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
print(f"   Path set to: {pytesseract.pytesseract.pytesseract_cmd}")

# Check 2: File exists
print("\n2️⃣ Checking if Tesseract executable exists...")
if os.path.exists(pytesseract.pytesseract.pytesseract_cmd):
    print(f"   ✅ File found: {pytesseract.pytesseract.pytesseract_cmd}")
else:
    print(f"   ❌ File NOT found at: {pytesseract.pytesseract.pytesseract_cmd}")
    print("\n   Try these alternative paths:")
    alt_paths = [
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Users\MAXxPAYNE\AppData\Local\Tesseract-OCR\tesseract.exe',
    ]
    for path in alt_paths:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"   {exists} {path}")

# Check 3: Version
print("\n3️⃣ Checking Tesseract version...")
try:
    result = pytesseract.get_tesseract_version()
    print(f"   ✅ Version: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 4: Test OCR on simple image
print("\n4️⃣ Testing OCR on simple image...")
try:
    # Create test image with text
    img = Image.new('RGB', (400, 100), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "SERVICE AGREEMENT", fill='black')
    
    # Try OCR
    text = pytesseract.image_to_string(img)
    print(f"   ✅ OCR Success!")
    print(f"   Extracted: '{text.strip()}'")
except Exception as e:
    print(f"   ❌ OCR Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)