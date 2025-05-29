import pandas as pd
import os, re

# 1) Helper to slugify college names
def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)  # non‑alnum → underscore
    return s.strip('_')

# 2) Load main college list
main_df = pd.read_csv("NEW_COLLEGE_DATA.csv")

# 3) Load your image‑status workbook (CSV or Excel)
#    Replace with the correct path/filename.
status_df = pd.read_excel("image_status.xlsx")  

# 4) Create slugs
main_df["SLUG"]   = main_df["COLLEGE"].apply(slugify)
status_df["SLUG"] = status_df["college list"].apply(slugify)

# 5) Deduplicate status_df by SLUG, keeping rows marked 'done' preferentially
#    First, mark any non‑'done' as False
status_df["DONE_FLAG"] = status_df["check"].str.lower() == "done"

#    Sort so that DONE_FLAG=True comes first, then drop duplicates
status_df = status_df.sort_values("DONE_FLAG", ascending=False)
status_df = status_df.drop_duplicates("SLUG", keep="first")

# 6) List actual image files in your images/ folder
image_files = os.listdir("images")
file_slugs = {os.path.splitext(f)[0] for f in image_files}

# 7) Merge main + status on SLUG
merged = main_df.merge(
    status_df[["SLUG", "DONE_FLAG"]],
    on="SLUG",
    how="left"
)

# 8) Generate IMAGE_PATH and HAS_IMAGE
def make_image_path(slug, done_flag):
    if done_flag and slug in file_slugs:
        return f"images/{slug}.jpg"
    return ""

merged["IMAGE_PATH"] = merged.apply(
    lambda r: make_image_path(r["SLUG"], r["DONE_FLAG"]), axis=1
)
merged["HAS_IMAGE"] = merged["IMAGE_PATH"] != ""

# 9) Report mismatches for you to fix
#    (status says done but file missing)
missing_files = merged[(merged["DONE_FLAG"]) & (~merged["HAS_IMAGE"])]
if not missing_files.empty:
    print("⚠️ The following slugs are marked 'done' but no file was found in images/:")
    print(missing_files[["COLLEGE","SLUG"]].to_string(index=False))
else:
    print("✅ All 'done' images found in images/ folder.")

# 9b) Report any stray image files with no matching slug
extra_files = [slug for slug in file_slugs if slug not in set(merged["SLUG"])]
if extra_files:
    print("\n⚠️ These files are in images/ but no matching college slug found:")
    for slug in extra_files:
        print("  -", slug)

# 10) Save the merged CSV
merged.to_csv("COLLEGE_WITH_IMAGES4.csv", index=False)
print(f"\nSaved COLLEGE_WITH_IMAGES3.csv ({len(merged)} rows).")
print(f"Total with images: {merged['HAS_IMAGE'].sum()}")