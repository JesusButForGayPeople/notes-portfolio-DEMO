import os
import json
import shutil

PDF_FOLDER = "pdfs"
THUMBNAIL_FOLDER = "thumbnails"
JSON_FILE = "pdfs.json"

def load_pdfs():
    """Load the existing PDF list from pdfs.json."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_pdfs(data):
    """Save the updated PDF list to pdfs.json."""
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

def list_pdfs(pdfs):
    """Prints the list of stored PDFs with numbers."""
    if not pdfs:
        print("No PDFs found in pdfs.json.")
        return None

    print("\nStored PDFs:")
    for i, pdf in enumerate(pdfs, start=1):
        print(f"{i}. {pdf['file']}")

    while True:
        try:
            choice = int(input("\nEnter the number of the PDF to rename: "))
            if 1 <= choice <= len(pdfs):
                return pdfs[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def rename_pdf(old_pdf_entry):
    """Renames a selected PDF and updates associated files."""
    old_name = old_pdf_entry["file"]
    old_pdf_path = os.path.join(PDF_FOLDER, old_name)

    old_thumb_name = old_pdf_entry["thumbnail"]
    old_thumb_path = os.path.join(THUMBNAIL_FOLDER, old_thumb_name)

    new_base_name = input("\nEnter the new name for the PDF (without .pdf): ").strip()
    new_name = f"{new_base_name}.pdf"
    new_pdf_path = os.path.join(PDF_FOLDER, new_name)

    new_thumb_name = f"{new_base_name}.png".replace(" ", "_")
    new_thumb_path = os.path.join(THUMBNAIL_FOLDER, new_thumb_name)

    # Ensure the new name doesn't already exist
    if os.path.exists(new_pdf_path):
        print("Error: A PDF with that name already exists.")
        return

    # Rename PDF file
    shutil.move(old_pdf_path, new_pdf_path)
    print(f"Renamed PDF: {old_name} → {new_name}")

    # Rename thumbnail if it exists
    if os.path.exists(old_thumb_path):
        shutil.move(old_thumb_path, new_thumb_path)
        print(f"Renamed Thumbnail: {old_thumb_name} → {new_thumb_name}")

    # Update JSON
    pdf_data = load_pdfs()
    for pdf in pdf_data:
        if pdf["file"] == old_name:
            pdf["file"] = new_name
            pdf["name"] = new_base_name
            pdf["thumbnail"] = new_thumb_name

    save_pdfs(pdf_data)
    print("Updated pdfs.json successfully!")

if __name__ == "__main__":
    pdf_list = load_pdfs()

    if not pdf_list:
        print("No PDFs available for renaming.")
    else:
        selected_pdf = list_pdfs(pdf_list)
        if selected_pdf:
            rename_pdf(selected_pdf)
