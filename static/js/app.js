// KevCal - Face Swap Calendar Generator JavaScript

let uploadedFiles = [];
let currentJobId = null;

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadedFilesDiv = document.getElementById('uploaded-files');
const generateBtn = document.getElementById('generate-btn');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultsSection = document.getElementById('results-section');
const resultsGrid = document.getElementById('results-grid');
const createProductBtn = document.getElementById('create-product-btn');
const downloadAllBtn = document.getElementById('download-all-btn');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkPrintfulConnection();
});

function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // Generate button
    generateBtn.addEventListener('click', generateCalendar);

    // Create product button
    createProductBtn.addEventListener('click', createPrintfulProduct);

    // Download all button
    downloadAllBtn.addEventListener('click', downloadAllImages);
}

async function checkPrintfulConnection() {
    try {
        const response = await fetch('/api/printful/verify');
        const data = await response.json();

        if (data.connected) {
            statusIndicator.textContent = '✅';
            statusText.textContent = 'Printful connected successfully';
        } else {
            statusIndicator.textContent = '❌';
            statusText.textContent = `Printful error: ${data.message}`;
        }
    } catch (error) {
        statusIndicator.textContent = '❌';
        statusText.textContent = 'Failed to check Printful connection';
    }
}

function handleFileSelect(e) {
    handleFiles(e.target.files);
}

function handleFiles(files) {
    if (uploadedFiles.length >= 3) {
        alert('Maximum 3 files allowed');
        return;
    }

    const remainingSlots = 3 - uploadedFiles.length;
    const filesToAdd = Array.from(files).slice(0, remainingSlots);

    filesToAdd.forEach(file => {
        if (file.type.startsWith('image/')) {
            uploadFile(file);
        }
    });
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();

        uploadedFiles.push({
            id: data.file_id,
            name: data.filename,
            url: URL.createObjectURL(file)
        });

        renderUploadedFiles();
        updateGenerateButton();

    } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload file');
    }
}

function renderUploadedFiles() {
    uploadedFilesDiv.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-preview">
            <img src="${file.url}" alt="${file.name}">
            <div class="file-name">${file.name}</div>
            <button class="remove-file" onclick="removeFile(${index})">×</button>
        </div>
    `).join('');
}

function removeFile(index) {
    URL.revokeObjectURL(uploadedFiles[index].url);
    uploadedFiles.splice(index, 1);
    renderUploadedFiles();
    updateGenerateButton();
}

function updateGenerateButton() {
    generateBtn.disabled = uploadedFiles.length === 0;
}

async function generateCalendar() {
    if (uploadedFiles.length === 0) return;

    // Use first uploaded file as source
    const sourceFileId = uploadedFiles[0].id;

    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Starting calendar generation...';
    generateBtn.disabled = true;

    try {
        // Start generation
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `source_file_id=${sourceFileId}`
        });

        if (!response.ok) throw new Error('Generation failed');

        const data = await response.json();
        currentJobId = data.job_id;

        // Poll for progress
        pollJobStatus(currentJobId);

    } catch (error) {
        console.error('Generation error:', error);
        alert('Failed to generate calendar');
        progressContainer.style.display = 'none';
        generateBtn.disabled = false;
    }
}

async function pollJobStatus(jobId) {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/job/${jobId}`);
            const job = await response.json();

            // Update progress
            progressFill.style.width = `${job.progress}%`;
            progressText.textContent = `Processing: ${job.progress}%`;

            if (job.status === 'completed') {
                clearInterval(pollInterval);
                progressText.textContent = 'Calendar generated successfully!';
                displayResults(job.images);
                generateBtn.disabled = false;
            } else if (job.status === 'failed') {
                clearInterval(pollInterval);
                alert(`Generation failed: ${job.error}`);
                progressContainer.style.display = 'none';
                generateBtn.disabled = false;
            }

        } catch (error) {
            clearInterval(pollInterval);
            console.error('Polling error:', error);
            alert('Failed to check generation status');
            progressContainer.style.display = 'none';
            generateBtn.disabled = false;
        }
    }, 1000); // Poll every second
}

function displayResults(images) {
    resultsSection.style.display = 'block';
    resultsGrid.innerHTML = images.map(img => `
        <div class="result-card">
            <img src="${img.url}" alt="${img.theme}">
            <div class="result-info">
                <div class="result-month">Month ${img.month}</div>
                <div class="result-theme">${img.theme}</div>
                <a href="${img.url}" download class="btn btn-secondary result-download">
                    Download Image
                </a>
            </div>
        </div>
    `).join('');

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

async function createPrintfulProduct() {
    if (!currentJobId) return;

    createProductBtn.disabled = true;
    createProductBtn.textContent = 'Creating product...';

    try {
        const response = await fetch(`/api/printful/create-product?job_id=${currentJobId}`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error('Failed to create product');

        const data = await response.json();

        alert('Printful calendar product created successfully! Check your Printful dashboard.');
        console.log('Printful product:', data);

    } catch (error) {
        console.error('Printful error:', error);
        alert(`Failed to create Printful product: ${error.message}`);
    } finally {
        createProductBtn.disabled = false;
        createProductBtn.textContent = 'Create Printful Calendar Product';
    }
}

function downloadAllImages() {
    const images = resultsGrid.querySelectorAll('img');
    images.forEach((img, index) => {
        setTimeout(() => {
            const a = document.createElement('a');
            a.href = img.src;
            a.download = `calendar_month_${index + 1}.jpg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }, index * 500); // Stagger downloads
    });
}
