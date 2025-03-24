document.addEventListener("DOMContentLoaded", async () => {
  const pdfContainer = document.getElementById("pdf-container");

  // Fetch the list of PDFs (from server or static JSON)
  const response = await fetch("pdfs.json");
  const pdfs = await response.json();

  pdfs.forEach((pdf) => {
    const pdfItem = document.createElement("div");
    pdfItem.classList.add("pdf-item");

    // Create a link for the thumbnail
    const thumbLink = document.createElement("a");
    thumbLink.href = `pdfs/${pdf.file}`;
    thumbLink.target = "_blank"; // Open in a new tab

    // Create the thumbnail image
    const img = document.createElement("img");
    img.src = `thumbnails/${pdf.thumbnail}`; // Thumbnail preview
    img.alt = pdf.name;

    // Append the thumbnail inside the link
    thumbLink.appendChild(img);

    // Create a link for the title
    const titleLink = document.createElement("a");
    titleLink.href = `pdfs/${pdf.file}`;
    titleLink.textContent = pdf.name;
    titleLink.target = "_blank"; // Open in a new tab

    // Append everything to the PDF item container
    pdfItem.appendChild(thumbLink); // Clickable thumbnail
    pdfItem.appendChild(titleLink); // Clickable title
    pdfContainer.appendChild(pdfItem);
  });
});
