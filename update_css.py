import os
import glob

# Files to update
files = glob.glob("*.html")

img_minified = "img{max-width:100%;height:auto;display:block}"
img_spaced = "img {\n      max-width: 100%;\n      height: auto;\n      display: block\n    }"
img_spaced2 = "    img {\n      max-width: 100%;\n      height: auto;\n      display: block\n    }"

img_new = """img {
  max-width: 100%;
  height: auto;
  display: block;
  /* Stops mobile scrolling flicker/jiggling */
  backface-visibility: hidden;
  transform: translateZ(0);
}"""

lead_img_minified = "figure.lead-img{margin-bottom:8px;border:2px solid var(--ink)}"
lead_img_spaced = "figure.lead-img {\n      margin-bottom: 8px;\n      border: 2px solid var(--ink)\n    }"
lead_img_spaced2 = "    figure.lead-img {\n      margin-bottom: 8px;\n      border: 2px solid var(--ink)\n    }"

lead_img_new = """figure.lead-img {
  margin-bottom: 8px;
  border: 2px solid var(--ink);
  overflow: hidden; /* Keeps image strictly contained */
}

figure.lead-img img {
  width: 100%;
  height: auto;
  aspect-ratio: 16/9; /* Prevents scroll jumping (CLS) before load */
  object-fit: cover;
}"""

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    updated = False
    if img_minified in content:
        content = content.replace(img_minified, img_new)
        updated = True
    elif img_spaced in content:
        content = content.replace(img_spaced, img_new)
        updated = True
    elif img_spaced2 in content:
        content = content.replace(img_spaced2, img_new)
        updated = True

    if lead_img_minified in content:
        content = content.replace(lead_img_minified, lead_img_new)
        updated = True
    elif lead_img_spaced in content:
        content = content.replace(lead_img_spaced, lead_img_new)
        updated = True
    elif lead_img_spaced2 in content:
        content = content.replace(lead_img_spaced2, lead_img_new)
        updated = True
        
    if updated:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
