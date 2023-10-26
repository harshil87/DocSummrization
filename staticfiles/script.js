const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');

// dropArea.addEventListener('dragover', (e) => {
//   e.preventDefault();
//   dropArea.style.borderColor = 'blue';
// });

// dropArea.addEventListener('dragleave', () => {
//   dropArea.style.borderColor = '#ccc';
// });

// dropArea.addEventListener('drop', (e) => {
//   e.preventDefault();
//   dropArea.style.borderColor = '#ccc';

//   const files = e.dataTransfer.files;
//   handleFiles(files);
// });

dropArea.addEventListener('click', () => {
  fileInput.click();
});

fileInput.addEventListener('change', () => {
  const files = fileInput.files;
  handleFiles(files);
});

function handleFiles(files) {
  for (const file of files) {
    const allowedExtensions = ["pdf", "docx"];
    const fileExtension = file.name.split(".").pop().toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
      alert("Unsupported file format: " + file.name);
      continue;
    }

    const fileItem = document.createElement('li');
    fileItem.className = 'file-item';
    fileItem.textContent = file.name;
    fileList.appendChild(fileItem);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const readMoreLinks = document.querySelectorAll(".read-more");

  readMoreLinks.forEach(link => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const content = this.parentElement.querySelector(".summary");
      if (content.style.display === "none" || content.style.display === "") {
        content.style.display = "block";
        this.textContent = "Read Less";
      } else {
        content.style.display = "none";
        this.textContent = "See Summary";
      }
    });
  });
});
