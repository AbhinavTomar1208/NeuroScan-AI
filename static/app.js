// DOM Elements
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const uploadPrompt = document.getElementById('upload-prompt');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const btnRemove = document.getElementById('btn-remove');
const btnClear = document.getElementById('btn-clear');
const btnAnalyze = document.getElementById('btn-analyze');
const sampleGrid = document.getElementById('sample-grid');

const resultsCard = document.getElementById('results-card');
const resultsPlaceholder = document.getElementById('results-placeholder');
const resultsContent = document.getElementById('results-content');
const diagnosisVal = document.getElementById('diagnosis-val');
const confidenceVal = document.getElementById('confidence-val');

// Chart Elements
const barNon = document.getElementById('bar-non');
const barVeryMild = document.getElementById('bar-very-mild');
const barMild = document.getElementById('bar-mild');
const barMod = document.getElementById('bar-mod');

const labelProbNon = document.getElementById('label-prob-non');
const labelProbVeryMild = document.getElementById('label-prob-very-mild');
const labelProbMild = document.getElementById('label-prob-mild');
const labelProbMod = document.getElementById('label-prob-mod');

// Recommendation Elements
const recTitle = document.getElementById('rec-title');
const recText = document.getElementById('rec-text');
const recommendationCard = document.getElementById('recommendation-card');

// History Elements
const historyList = document.getElementById('history-list');
const btnClearHistory = document.getElementById('btn-clear-history');

// App State
let selectedFile = null;
let selectedFileBase64 = null; // Store base64 representation for history loading

// Diagnosis Clinical Descriptions
const CLINICAL_GUIDE = {
    'Non Demented': {
        title: "Cognitive Status: Healthy Brain Profile",
        text: "The AI analysis indicates no detectable patterns of dementia. The structural features match a healthy age-appropriate brain profile. Maintain healthy lifestyle factors including regular exercise, a balanced diet, and cognitive engagement to support long-term brain health.",
        classColor: 'status-non',
        cardBorder: 'var(--color-non)'
    },
    'Very Mild Demented': {
        title: "Cognitive Status: Early Warning / Mild Impairment",
        text: "The model detected subtle indicators consistent with early cognitive changes (often classified as Mild Cognitive Impairment or MCI). While daily routines are generally preserved, it is recommended to discuss these findings with a medical professional for comprehensive cognitive testing.",
        classColor: 'status-very-mild',
        cardBorder: 'var(--color-very-mild)'
    },
    'Mild Demented': {
        title: "Cognitive Status: Mild Cognitive Decline",
        text: "Model patterns indicate structural features characteristic of mild Alzheimer's disease. These findings are often associated with minor difficulties in daily tasks, planning, and memory retrieval. Consult a neurologist for a detailed assessment and discussion of supportive care options.",
        classColor: 'status-mild',
        cardBorder: 'var(--color-mild)'
    },
    'Moderate Demented': {
        title: "Cognitive Status: Moderate Cognitive Decline",
        text: "The scan reveals significant structural changes consistent with moderate Alzheimer's disease, including notable volume loss in critical memory-related areas. Prioritize clinical evaluations, neurologist consultations, and establishing supportive care networks.",
        classColor: 'status-mod',
        cardBorder: 'var(--color-mod)'
    }
};

// Initialize app
window.addEventListener('DOMContentLoaded', () => {
    loadHistoryFromStorage();
    setupUploadHandlers();
    setupSampleHandlers();
    setupHistoryHandlers();
});

// Setup drag and drop + click upload
function setupUploadHandlers() {
    uploadZone.addEventListener('click', () => {
        if (!selectedFile) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation(); // Avoid triggering file selection click
        clearUpload();
    });

    btnClear.addEventListener('click', clearUpload);

    btnAnalyze.addEventListener('click', runAnalysis);
}

// Setup quick test sample image clicks
function setupSampleHandlers() {
    sampleGrid.addEventListener('click', async (e) => {
        const sampleCard = e.target.closest('.sample-card');
        if (!sampleCard) return;

        const sampleKey = sampleCard.dataset.sample;
        const filename = `${sampleKey}.png`;
        const filepath = `samples/${filename}`;

        try {
            btnAnalyze.disabled = true;
            sampleCard.classList.add('loading-pulse');
            
            // Fetch sample image and convert it to a file object
            const response = await fetch(filepath);
            if (!response.ok) {
                throw new Error("Sample file not found on server.");
            }
            const blob = await response.blob();
            const file = new File([blob], filename, { type: 'image/png' });
            
            sampleCard.classList.remove('loading-pulse');
            handleFileSelect(file);
        } catch (err) {
            sampleCard.classList.remove('loading-pulse');
            alert("Failed to load sample image: " + err.message);
            btnAnalyze.disabled = selectedFile === null;
        }
    });
}

// Setup history controls
function setupHistoryHandlers() {
    btnClearHistory.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm('Are you sure you want to delete all history records? This action cannot be undone.')) {
            clearAllHistory();
        }
    });
}

// Clear all history records
function clearAllHistory() {
    localStorage.removeItem('alz_diagnostic_history');
    renderHistory([]);
    console.log("All history records cleared.");
}

// Delete a specific history record
function deleteHistoryRecord(id) {
    let history = JSON.parse(localStorage.getItem('alz_diagnostic_history')) || [];
    history = history.filter(item => item.id !== id);
    localStorage.setItem('alz_diagnostic_history', JSON.stringify(history));
    renderHistory(history);
}

// Handle file processing and display
function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        alert("Please select a valid image file (PNG/JPEG).");
        return;
    }

    selectedFile = file;

    // Read image as Data URL for preview and history persistence
    const reader = new FileReader();
    reader.onload = (e) => {
        selectedFileBase64 = e.target.result;
        previewImage.src = selectedFileBase64;
        
        // UI shifts
        uploadPrompt.style.display = 'none';
        previewContainer.style.display = 'flex';
        
        // Enable buttons
        btnAnalyze.disabled = false;
        btnClear.disabled = false;
    };
    reader.readAsDataURL(file);
}

// Reset upload and preview UI
function clearUpload() {
    selectedFile = null;
    selectedFileBase64 = null;
    fileInput.value = '';
    
    // UI shifts
    uploadPrompt.style.display = 'flex';
    previewContainer.style.display = 'none';
    previewContainer.classList.remove('scanning');
    previewImage.src = '';
    
    // Reset controls
    btnAnalyze.disabled = true;
    btnClear.disabled = true;
    
    // Reset result panel to placeholder
    resultsPlaceholder.style.display = 'flex';
    resultsContent.style.display = 'none';
}

// Send prediction API request to backend
async function runAnalysis() {
    if (!selectedFile) return;

    // Update UI state to loading / scanning
    previewContainer.classList.add('scanning');
    btnAnalyze.disabled = true;
    btnClear.disabled = true;
    btnRemove.style.display = 'none';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.predicted_class, data.confidence, data.predictions);
            saveToSessionHistory(data.predicted_class, data.confidence, selectedFileBase64);
        } else {
            alert("Analysis failed: " + data.error);
            clearUpload();
        }
    } catch (err) {
        console.error(err);
        alert("Server communication error. Please ensure the backend is running.");
        clearUpload();
    } finally {
        // Remove loading state
        previewContainer.classList.remove('scanning');
        btnAnalyze.disabled = false;
        btnClear.disabled = false;
        btnRemove.style.display = 'flex';
    }
}

// Display prediction outputs in result card
function displayResults(predictedClass, confidence, predictions) {
    // Hide empty state
    resultsPlaceholder.style.display = 'none';
    resultsContent.style.display = 'block';

    // Set class name & confidence
    diagnosisVal.textContent = predictedClass;
    
    // Reset classes and apply class-specific color
    diagnosisVal.className = 'diagnosis-value';
    const guide = CLINICAL_GUIDE[predictedClass];
    if (guide) {
        diagnosisVal.classList.add(guide.classColor);
        recTitle.textContent = guide.title;
        recText.textContent = guide.text;
        recommendationCard.style.borderLeftColor = guide.cardBorder;
    }

    confidenceVal.textContent = (confidence * 100).toFixed(1) + '%';

    // Set bar chart widths and percentage text
    animateChartBar(barNon, labelProbNon, predictions['Non Demented']);
    animateChartBar(barVeryMild, labelProbVeryMild, predictions['Very Mild Demented']);
    animateChartBar(barMild, labelProbMild, predictions['Mild Demented']);
    animateChartBar(barMod, labelProbMod, predictions['Moderate Demented']);
}

function animateChartBar(barElement, labelElement, value) {
    const percentageStr = (value * 100).toFixed(1) + '%';
    labelElement.textContent = percentageStr;
    
    // Brief delay to trigger transition smoothly
    setTimeout(() => {
        barElement.style.width = percentageStr;
    }, 50);
}

// Save history in LocalStorage
function saveToSessionHistory(predictedClass, confidence, imageBase64) {
    const historyItem = {
        id: Date.now(),
        predictedClass,
        confidence,
        imageBase64,
        date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ', ' + new Date().toLocaleDateString()
    };

    let history = JSON.parse(localStorage.getItem('alz_diagnostic_history')) || [];
    // Insert at front
    history.unshift(historyItem);
    
    // Limit to last 6 entries
    if (history.length > 6) {
        history.pop();
    }

    localStorage.setItem('alz_diagnostic_history', JSON.stringify(history));
    renderHistory(history);
}

// Load history from storage
function loadHistoryFromStorage() {
    let history = JSON.parse(localStorage.getItem('alz_diagnostic_history')) || [];
    renderHistory(history);
}

// Render history entries
function renderHistory(history) {
    // Show or hide clear history button
    if (history.length === 0) {
        btnClearHistory.style.display = 'none';
        historyList.innerHTML = `<div class="history-empty">No clinical logs saved in this session. Runs will save locally.</div>`;
        return;
    }

    btnClearHistory.style.display = 'flex';

    historyList.innerHTML = history.map(item => {
        const guide = CLINICAL_GUIDE[item.predictedClass];
        const colorClass = guide ? guide.classColor : '';
        return `
            <div class="history-item" data-id="${item.id}">
                <div class="history-thumb">
                    <img src="${item.imageBase64}" alt="MRI Thumbnail">
                </div>
                <div class="history-info">
                    <h4>${item.predictedClass}</h4>
                    <p>${item.date}</p>
                </div>
                <div class="history-meta">
                    <span class="badge ${colorClass}">${(item.confidence * 100).toFixed(0)}%</span>
                    <button class="history-delete-btn" data-id="${item.id}" title="Delete this record">
                        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    // Setup history item click events (for loading)
    const items = historyList.querySelectorAll('.history-item');
    items.forEach(el => {
        el.addEventListener('click', (e) => {
            // Don't load if clicking the delete button
            if (!e.target.closest('.history-delete-btn')) {
                const id = parseInt(el.dataset.id);
                const record = history.find(r => r.id === id);
                if (record) {
                    loadHistoryRecord(record);
                }
            }
        });
    });

    // Setup delete button click events
    const deleteButtons = historyList.querySelectorAll('.history-delete-btn');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            if (confirm('Delete this scan record?')) {
                deleteHistoryRecord(id);
            }
        });
    });
}

// Load historical record back into UI
function loadHistoryRecord(record) {
    // Set up the preview image
    selectedFileBase64 = record.imageBase64;
    previewImage.src = record.imageBase64;
    uploadPrompt.style.display = 'none';
    previewContainer.style.display = 'flex';
    
    btnAnalyze.disabled = false;
    btnClear.disabled = false;

    // Convert Base64 back to file structure so "Run Diagnostics" works again if they re-click it
    selectedFile = dataURLtoFile(record.imageBase64, 'restored_mri.png');

    // Run prediction visualization reload
    runAnalysis();
}

// Helper to convert base64 image data to File object
function dataURLtoFile(dataurl, filename) {
    var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
}
