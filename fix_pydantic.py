import glob

files = glob.glob(r"c:\Users\Muneesha\Desktop\Nurofin Executive AI\Nurofin-ai-backend\app\schemas\*.py")
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if "from_attributes = True" in content:
        new_content = content.replace("from_attributes = True", "orm_mode = True")
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated {f}")
print("Done")
