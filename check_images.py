
import pandas as pd
import os

DATA_PATH = "parts_data.csv"
IMG_DIR = "quality_images"

def check_image_health(filename):
    if pd.isna(filename) or str(filename).strip() == "":
        return "SKIP", None
    
    fname = str(filename).strip()
    path = os.path.join(IMG_DIR, fname)
    
    if not os.path.exists(path):
        return "MISSING", path
        
    try:
        if os.path.getsize(path) == 0:
            return "EMPTY (0 bytes)", path
    except OSError:
        return "ERROR", path
        
    return "OK", path

def main():
    print("--- Starting Image Audit ---")
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Rename maps matching app.py logic roughly, or just check columns by name
    # app.py remaps: '標準重量(g)': '重量', ... '異常履歷寫真1': '異常履歷寫真'
    # But current CSV headers are likely: 產品圖片, 異常履歷寫真1, 異常履歷寫真2, 異常履歷寫真3
    
    img_cols = ['產品圖片', '異常履歷寫真1', '異常履歷寫真2', '異常履歷寫真3']
    
    results = {"OK": 0, "MISSING": 0, "EMPTY": 0, "SKIP": 0}
    problems = []

    for index, row in df.iterrows():
        part_no = row.get('品番', f'Row {index}')
        
        for col in img_cols:
            if col in df.columns:
                status, path = check_image_health(row[col])
                
                if status == "SKIP":
                    results["SKIP"] += 1
                elif status == "OK":
                    results["OK"] += 1
                else:
                    if "EMPTY" in status: results["EMPTY"] += 1
                    if "MISSING" in status: results["MISSING"] += 1
                    
                    problems.append(f"[{status}] Part: {part_no} | Col: {col} | File: {row[col]}")

    print("\n--- Audit Results ---")
    print(f"Total Images Checked: {sum(results.values()) - results['SKIP']}")
    print(f"OK: {results['OK']}")
    print(f"MISSING: {results['MISSING']}")
    print(f"EMPTY (0 bytes): {results['EMPTY']}")
    
    if problems:
        print("\n--- Problems Found ---")
        for p in problems:
            print(p)
    else:
        print("\n✅ No image problems found!")

if __name__ == "__main__":
    main()
