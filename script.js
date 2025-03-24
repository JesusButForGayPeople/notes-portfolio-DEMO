document.addEventListener("DOMContentLoaded", async () => {
  const pdfContainer = document.getElementById("pdf-container");

  try {
    const response = await fetch("pdfs.json");
    if (!response.ok) throw new Error("Failed to load pdfs.json");

    const pdfs = await response.json();
    pdfs.forEach((pdf) => {
      const pdfItem = document.createElement("div");
      pdfItem.classList.add("pdf-item");

      const thumbLink = document.createElement("a");
      thumbLink.href = `pdfs/${encodeURIComponent(pdf.file)}`;
      thumbLink.target = "_blank";

      const img = document.createElement("img");
      img.src = `thumbnails/${encodeURIComponent(pdf.thumbnail)}`;
      img.alt = pdf.name;

      thumbLink.appendChild(img);

      const titleLink = document.createElement("a");
      titleLink.href = `pdfs/${encodeURIComponent(pdf.file)}`;
      titleLink.textContent = pdf.name;
      titleLink.target = "_blank";

      pdfItem.appendChild(thumbLink);
      pdfItem.appendChild(titleLink);
      pdfContainer.appendChild(pdfItem);
    });
  } catch (error) {
    console.error("Error loading PDFs:", error);
  }
});
