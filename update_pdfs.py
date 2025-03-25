import os
import json
import subprocess
import argparse

PDF_FOLDER = "pdfs"
THUMBNAIL_FOLDER = "thumbnails"
JSON_FILE = "pdfs.json"

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate and manage PDF thumbnails.")
parser.add_argument("--regen", action="store_true", help="Delete existing thumbnails and regenerate them.")
args = parser.parse_args()

# Ensure directories exist
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

# If --regen flag is set, delete all existing thumbnails
if args.regen:
    print("Regenerating all thumbnails...")
    for file in os.listdir(THUMBNAIL_FOLDER):
        os.remove(os.path.join(THUMBNAIL_FOLDER, file))
    print("All thumbnails deleted.")

# Load existing data from pdfs.json
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r") as f:
        try:
            existing_pdfs = json.load(f)
        except json.JSONDecodeError:
            existing_pdfs = []
else:
    existing_pdfs = []

# Create lookup dictionaries for existing data
existing_pdf_files = {pdf["file"] for pdf in existing_pdfs}
existing_thumbnail_files = {pdf["thumbnail"] for pdf in existing_pdfs}

# Get current PDF files in the folder
current_pdf_files = {f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")}

# Process all current PDF files
updated_pdfs = []

for pdf_file in current_pdf_files:
    pdf_path = os.path.join(PDF_FOLDER, pdf_file)
    thumbnail_name = pdf_file.replace(" ", "_").replace(".pdf", ".png")
    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_name)

    # Check if we need to generate a new thumbnail
    need_new_thumbnail = (
        args.regen or
        thumbnail_name not in existing_thumbnail_files or
        not os.path.exists(thumbnail_path)
    )

    if need_new_thumbnail:
        print(f"Generating thumbnail for: {pdf_file}")
        try:
            result = subprocess.run([
                "magick", "-density", "300", pdf_path + "[0]",
                "-background", "white", "-flatten", "-alpha", "off",
                "-resize", "800x800", thumbnail_path
            ], capture_output=True, text=True, check=True)

            if result.stderr:
                print(f"ImageMagick warning for {pdf_file}: {result.stderr.strip()}")

            print(f"Thumbnail created: {thumbnail_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error generating thumbnail for {pdf_file}: {e.stderr.strip()}")
            continue

    # Add to the updated list
    updated_pdfs.append({
        "name": pdf_file.replace(".pdf", ""),
        "file": pdf_file,
        "thumbnail": thumbnail_name
    })

# Clean up orphaned thumbnails (thumbnails without corresponding PDFs)
current_thumbnail_files = {pdf["thumbnail"] for pdf in updated_pdfs}
for thumbnail in os.listdir(THUMBNAIL_FOLDER):
    if thumbnail not in current_thumbnail_files:
        os.remove(os.path.join(THUMBNAIL_FOLDER, thumbnail))
        print(f"Deleted orphaned thumbnail: {thumbnail}")

# Save updated JSON file
with open(JSON_FILE, "w") as f:
    json.dump(updated_pdfs, f, indent=4)

print(f"✅ Successfully updated {JSON_FILE} with {len(updated_pdfs)} PDFs!")
