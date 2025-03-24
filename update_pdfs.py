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

# Ensure thumbnails directory exists
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

# Convert existing JSON data into a dictionary for quick lookup
existing_pdf_data = {pdf["file"]: pdf for pdf in existing_pdfs}

# Get list of actual PDFs in the folder
pdf_files = set(f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf"))

# Reset the existing thumbnails list after deletion (if --regen was used)
existing_thumbnails = set(os.listdir(THUMBNAIL_FOLDER)) if not args.regen else set()

updated_pdfs = []

for pdf_file in pdf_files:
    pdf_path = os.path.join(PDF_FOLDER, pdf_file)
    thumbnail_name = pdf_file.replace(" ", "_").replace(".pdf", ".png")
    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, thumbnail_name)

    # Generate a new thumbnail if it doesn't exist or --regen was used
    if args.regen or thumbnail_name not in existing_thumbnails:
        print(f"Generating thumbnail for: {pdf_file}")
        try:
            result = subprocess.run([
                "magick", "-density", "300", pdf_path + "[0]",
                "-background", "white", "-flatten", "-alpha", "off",
                "-resize", "800x800", thumbnail_path
            ], capture_output=True, text=True, check=True)

            # Print any warnings from ImageMagick
            if result.stderr:
                print(f"ImageMagick warning for {pdf_file}: {result.stderr.strip()}")

            print(f"Thumbnail created: {thumbnail_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error generating thumbnail for {pdf_file}: {e.stderr.strip()}")
            continue  # Skip this file and move on

    # Update JSON entry
    updated_pdfs.append({
        "name": pdf_file.replace(".pdf", ""),
        "file": pdf_file,
        "thumbnail": thumbnail_name
    })

# Remove outdated thumbnails (if they belong to deleted PDFs)
for thumbnail in os.listdir(THUMBNAIL_FOLDER):
    expected_pdf = thumbnail.replace("_", " ").replace(".png", ".pdf")
    if expected_pdf not in pdf_files:
        os.remove(os.path.join(THUMBNAIL_FOLDER, thumbnail))
        print(f"Deleted orphaned thumbnail: {thumbnail}")

# Save updated JSON file (only keeping valid PDFs)
with open(JSON_FILE, "w") as f:
    json.dump(updated_pdfs, f, indent=4)

print("✅ Successfully updated pdfs.json, regenerated thumbnails (if needed), and cleaned up removed files!")
