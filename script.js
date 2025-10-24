// ========================================================================
// 1. DATA FILE PATHS
// ========================================================================
// Assuming these files are in the same folder on GitHub Pages
const TEXT_FILE_PATH = 'text.txt';
const VOCAB_FILE_PATH = 'vocab.json';


// ========================================================================
// 2. CORE JAVASCRIPT LOGIC
// ========================================================================

const textArea = document.getElementById('german-text-area');
const vocabList = document.getElementById('selected-vocab-list');
const vocabCountSpan = document.getElementById('vocab-count');
const clearButton = document.getElementById('clear-vocab-button');
// New constant for the definition display area
const definitionDisplay = document.getElementById('definition-display');

// Global variables to store the data once fetched
let germanText = '';
let vocabularyData = [];
let selectedVocab = JSON.parse(localStorage.getItem('selectedVocab')) || [];


/**
 * Fetches the text and JSON data, then initializes the app.
 */
async function loadDataAndInitializeApp() {
    try {
        // 1. Fetch German Text
        const textResponse = await fetch(TEXT_FILE_PATH);
        if (!textResponse.ok) throw new Error(`HTTP error! status: ${textResponse.status} for ${TEXT_FILE_PATH}`);
        germanText = await textResponse.text();

        // 2. Fetch Vocabulary JSON
        const vocabResponse = await fetch(VOCAB_FILE_PATH);
        if (!vocabResponse.ok) throw new Error(`HTTP error! status: ${vocabResponse.status} for ${VOCAB_FILE_PATH}`);
        vocabularyData = await vocabResponse.json();

        // 3. Sort Vocabulary for accurate matching (longer words first)
        vocabularyData.sort((a, b) => b.word.length - a.word.length);
        
        // 4. Initialize the UI
        renderInteractiveText();
        saveAndRenderVocab(); 

    } catch (error) {
        console.error("Failed to load application data:", error);
        textArea.innerHTML = `<p style="color: red;">Fehler beim Laden des Textes oder Vokabulars. Bitte prüfen Sie die Dateien ${TEXT_FILE_PATH} und ${VOCAB_FILE_PATH}.</p>`;
    }
}

/**
 * Replaces words in the text with clickable <span> elements.
 */
function renderInteractiveText() {
    if (!germanText || vocabularyData.length === 0) return;

    let newText = germanText;
    // ... (rest of the text parsing and wrapping logic remains the same) ...

    // Display the fully wrapped text in the HTML
    textArea.innerHTML = `<p>${newText.trim()}</p>`;

    // Attach new event listeners: mouseover for definition, click for adding
    document.querySelectorAll('.vocab-word').forEach(span => {
        span.addEventListener('mouseover', handleWordHover);
        span.addEventListener('click', handleWordClick); // Now handles ONLY the adding
    });
}

/**
 * Handles the MOUSEOVER event on a vocabulary word to display the definition.
 */
function handleWordHover(event) {
    const word = event.target.dataset.word;
    const vocabObject = vocabularyData.find(item => item.word === word);

    if (vocabObject) {
        definitionDisplay.innerHTML = `
            <strong>${vocabObject.word}</strong>
            <p>DE: ${vocabObject.definition_german}</p>
            <p>EN: ${vocabObject.definition_english}</p>
            <div class="definition-action">Klicken, um zum Vokabel-Set hinzuzufügen.</div>
        `;
    }
}

    // Display the fully wrapped text in the HTML
    textArea.innerHTML = `<p>${newText.trim()}</p>`;

    // Attach click listeners to all the new spans
    document.querySelectorAll('.vocab-word').forEach(span => {
        span.addEventListener('click', handleWordClick);
    });
}


/**
 * Handles the CLICK event on a vocabulary word to ADD it to the list.
 */
function handleWordClick(event) {
    const word = event.target.dataset.word;
    const vocabObject = vocabularyData.find(item => item.word === word);

    if (vocabObject) {
        // Check if the word is already in the selected list
        if (!selectedVocab.some(item => item.word === word)) {
            selectedVocab.push(vocabObject);
            saveAndRenderVocab();
            alert(`"${word}" wurde zum Set hinzugefügt!`); // Small confirmation alert
        } else {
            // If the word is already in the set, perhaps highlight it briefly instead of alerting
            event.target.style.backgroundColor = '#2ecc71'; // Green highlight
            setTimeout(() => {
                event.target.style.backgroundColor = ''; // Reset color
            }, 500);
        }
    }
}

/**
 * Saves the current selectedVocab array to localStorage and updates the sidebar.
 */
function saveAndRenderVocab() {
    // Save to the browser's storage
    localStorage.setItem('selectedVocab', JSON.stringify(selectedVocab));

    // Update the list count
    vocabCountSpan.textContent = selectedVocab.length;
    
    // Clear and re-render the list in the sidebar
    vocabList.innerHTML = '';
    
    if (selectedVocab.length === 0) {
        vocabList.innerHTML = '<li>Dein Set ist leer. Klicke Wörter im Text an, um sie hinzuzufügen.</li>';
        return;
    }

    selectedVocab.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
            <strong>${item.word}</strong>
            <p>DE: ${item.definition_german}</p>
            <p>EN: ${item.definition_english}</p>
        `;
        vocabList.appendChild(li);
    });
}

/**
 * Clears the selected vocabulary list.
 */
function clearVocabSet() {
    if (confirm("Möchtest du dein Vokabel-Set wirklich löschen?")) {
        selectedVocab = [];
        saveAndRenderVocab();
        alert("Vokabel-Set gelöscht!");
    }
}

// ========================================================================
// 3. INITIALIZATION
// ========================================================================

// Add the event listener for the clear button
clearButton.addEventListener('click', clearVocabSet);

// Start the entire process by loading the data
loadDataAndInitializeApp();
