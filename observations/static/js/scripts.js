document.addEventListener("DOMContentLoaded", function () {
    let selectedFiles = [];

    const form = document.getElementById("report-form");
    const fileInput = document.getElementById("image");

    fileInput.addEventListener("change", function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        Array.from(files).forEach(file => {
            if (!selectedFiles.some(f => f.name === file.name)) {
                selectedFiles.push(file);
            } else {
                alert(`Duplicate file: ${file.name}`);
            }
        });
        updateFileList();
    }

    function updateFileList() {
        const list = document.getElementById("file-list");
        list.innerHTML = "";
        selectedFiles.forEach((file, index) => {
            const li = document.createElement("li");
            li.innerHTML = `
                ${file.name}
                <button type="button" class="remove-btn" data-index="${index}">Remove</button>
            `;
            list.appendChild(li);
        });

        document.querySelectorAll(".remove-btn").forEach(btn =>
            btn.addEventListener("click", e => removeFile(e.target.dataset.index))
        );
    }

    function removeFile(index) {
        selectedFiles.splice(index, 1);
        updateFileList();
    }

    // Generate PDF on form submission
    document.getElementById("generate-report").addEventListener("click", function () {
        const authority = document.getElementById("authority").value;
        const crime = document.getElementById("crime").value;
        const firstName = document.getElementById("first-name").value.trim();
        const lastName = document.getElementById("last-name").value.trim();
        const email = document.getElementById("email").value.trim();

        if (!authority || !crime || !firstName || !lastName || !email) {
            alert("Please fill all required fields.");
            return;
        }

        if (selectedFiles.length < 1) {
            alert("Please upload at least one image.");
            return;
        }

        const formData = new FormData();
        formData.append("image", selectedFiles[0]);

        // Send the image to the backend for object detection
        fetch("/generate_report/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            generatePDF(authority, crime, firstName, lastName, email, data.detected_objects);
        })
        .catch(error => {
            alert("Error detecting objects: " + error);
        });
    });

    // Generate the PDF with object detection data
    function generatePDF(authority, crime, firstName, lastName, email, detectedObjects) {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        doc.setFont("helvetica", "bold");
        doc.setFontSize(18);
        doc.text("Crime Scene Observation Report", 20, 20);

        doc.setFont("helvetica", "normal");
        doc.setFontSize(12);
        doc.text(`Official Authority: ${authority}`, 20, 40);
        doc.text(`Crime Type: ${crime}`, 20, 50);
        doc.text(`First Name: ${firstName}`, 20, 60);
        doc.text(`Last Name: ${lastName}`, 20, 70);
        doc.text(`Email: ${email}`, 20, 80);
        doc.text(`Detected Objects: ${detectedObjects.length}`, 20, 90);

        let yOffset = 100;

        detectedObjects.forEach(object => {
            doc.text(`Object: ${object.class}, Confidence: ${object.score.toFixed(2)}`, 20, yOffset);
            yOffset += 10;
        });

        const filename = `${firstName}_${lastName}_${crime}_report.pdf`;
        doc.save(filename);
        alert("PDF report generated successfully!");
    }
});
