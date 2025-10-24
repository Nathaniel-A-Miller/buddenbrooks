// ========================================================================
// 0. FIREBASE CONFIGURATION 
// ========================================================================

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyB_dWt_OFudecBlmyjnl5-b69lNp77OB9w",
    authDomain: "buddenrbooks.firebaseapp.com",
    projectId: "buddenrbooks",
    storageBucket: "buddenrbooks.firebasestorage.app",
    messagingSenderId: "133066434831",
    appId: "1:133066434831:web:c7ea4f8ef5a8296181f67a"
};

let db; // ADDED: Declare globally with 'let'
let submissionsCollection; // ADDED: Declare globally with 'let'

// Initialize Firebase and Firestore
if (typeof firebase !== 'undefined' && !firebase.apps.length) {
    // FIX 1: Use firebase.initializeApp
    const app = firebase.initializeApp(firebaseConfig); 
    
    // FIX 2: Assign to the global 'db' and 'submissionsCollection' variables
    db = firebase.firestore();
    submissionsCollection = db.collection('submissions');
}

// ========================================================================
// 1. DATA FILE PATH
// ========================================================================
const VOCAB_FILE_PATH = 'vocab.json';


// ========================================================================
// 2. DOM ELEMENTS & GLOBAL VARIABLES
// ========================================================================

const textArea = document.getElementById('german-text-area');
const vocabList = document.getElementById('selected-vocab-list');
const vocabCountSpan = document.getElementById('vocab-count');
const clearButton = document.getElementById('clear-vocab-button');
const downloadButton = document.getElementById('download-vocab-button');
const definitionDisplay = document.getElementById('definition-display'); // New element
const chapterSelect = document.getElementById('chapter-select'); // <--- ADD THIS LINE
const submissionForm = document.getElementById('submission-form');
const submitWordInput = document.getElementById('submit-word');
const submissionMessage = document.getElementById('submission-message');
const submitDefinitionEnInput = document.getElementById('submit-definition-en');
const instructionsPanel = document.getElementById('instructions-panel');
const dismissButton = document.getElementById('dismiss-instructions');


let germanText = '';
let vocabularyData = [];
// Load selected words from the browser's local storage or start with an empty array
let selectedVocab = JSON.parse(localStorage.getItem('selectedVocab')) || [];
let availableChapters = []; // To store chapter numbers/titles
let currentChapter = 1;     // Start with Chapter 1


// ========================================================================
// 3. CORE FUNCTIONS
// ========================================================================

/**
 * Fetches the text and JSON data, then initializes the app.
 */
// script.js (Inside loadDataAndInitializeApp)

async function loadDataAndInitializeApp() {
    try {
        // ... (1. Fetch German Text)
        // You'll need to fetch the text for the currentChapter, not just 'chapter 1'.
        // For now, we'll assume a file path like `chapter_1.txt`, `chapter_2.txt`, etc.
        const textResponse = await fetch(`chapters/chapter_${currentChapter}.txt`); // 👈 IMPORTANT CHANGE
        if (!textResponse.ok) throw new Error(`HTTP error! status: ${textResponse.status}`);
        germanText = await textResponse.text();

        // 2. Fetch Vocabulary for the current chapter (Chapter 1)
        await fetchAndSetVocab(currentChapter);

        // 3. Extract unique chapters and populate the dropdown (NEW LOGIC)
        availableChapters = Array.from({length: 97}, (_, i) => i + 1);
        populateChapterDropdown(availableChapters); // Call new helper function
        
        // 4. Sort Vocabulary (Filter will happen in the rendering function)
        // ...

        // 5. Initialize the UI
        renderInteractiveText();
        saveAndRenderVocab();
        // Check if instructions need to be shown
        checkAndShowInstructions();

    } catch (error) {
        // ... error handling ...
    }
}
// script.js (New Helper Functions)

/**
 * Populates the <select> element with options for each chapter.
 */
function populateChapterDropdown(chapters) {
    chapterSelect.innerHTML = ''; // Clear existing options

    chapters.forEach(chapterNum => {
        const option = document.createElement('option');
        option.value = chapterNum;
        option.textContent = `Kapitel ${chapterNum}`;
        chapterSelect.appendChild(option);
    });
    
    // Set the initial value to Chapter 1
    chapterSelect.value = currentChapter;
}

// Function to fetch and set vocab for a chapter
async function fetchAndSetVocab(chapterNum) {
    
    // Fetch the specific chapter's vocabulary JSON
    const vocabResponse = await fetch(`vocab_data/vocab_ch${chapterNum}.json`);
    if (!vocabResponse.ok) throw new Error(`Vocab load error! status: ${vocabResponse.status}`);
    
    // vocabularyData now ONLY contains data for the current chapter
    vocabularyData = await vocabResponse.json(); 
    
    // Sort and render as usual
    vocabularyData.sort((a, b) => b.word.length - a.word.length);
    renderInteractiveText();
}

async function handleChapterChange(event) {
    const newChapter = parseInt(event.target.value);
    if (newChapter === currentChapter) return; // No change

    currentChapter = newChapter;
    
    // 1. Fetch the new chapter text
    try {
        const textResponse = await fetch(`chapters/chapter_${currentChapter}.txt`); // 👈 IMPORTANT
        if (!textResponse.ok) throw new Error(`HTTP error! status: ${textResponse.status}`);
        germanText = await textResponse.text();
        await fetchAndSetVocab(currentChapter);
        
    } catch (error) {
        console.error("Failed to load chapter text:", error);
        textArea.innerHTML = `<p style="color: red;">Fehler beim Laden von Kapitel ${currentChapter}.</p>`;
    }
}
/**
 * Converts the global selectedVocab array into a CSV string.
 * Uses localStorage data structure: { word: '...', definition: '...' }
 */
// script.js (Inside the convertArrayToCSV function)

function convertArrayToCSV(data) {
    if (data.length === 0) return '';
    
    // 1. Get Headers (Keys of the first object)
    const headers = ['Wort (DE)', 'Definition (DE)', 'Definition (EN)']; 
    const keys = ['word', 'definition', 'definitionEN'];
    
    let csv = headers.join(',') + '\n';

    // 2. Map Data Rows
    data.forEach(item => {
        const row = keys.map(key => {
            // FIX: Ensure 'val' is a string. If it's undefined/null, default to an empty string.
            let val = String(item[key] || ''); 
            
            // Check for characters that require quoting
            if (val.includes(',') || val.includes('"') || val.includes('\n')) {
                // Escape existing double quotes and wrap the entire string in quotes
                val = '"' + val.replace(/"/g, '""') + '"';
            }
            return val;
        });
        csv += row.join(',') + '\n';
    });
    
    return csv;
}

/**
 * Triggers the browser to download the CSV string as a file.
 */
// script.js (The downloadCSV function)

function downloadCSV(csvContent, filename) {
    const BOM = '\uFEFF'; 
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    
    // Programmatically click the hidden link to start the download
    document.body.appendChild(a); 
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
}

/**
 * Shows the instructions panel once per user, using localStorage.
 */
function checkAndShowInstructions() {
    // Check if the user has dismissed the instructions before
    if (localStorage.getItem('instructionsDismissed') !== 'true') {
        if (instructionsPanel) {
            instructionsPanel.style.display = 'block';
            
            // Add event listener to dismiss button
            if (dismissButton) {
                dismissButton.addEventListener('click', dismissInstructions);
            }
        }
    }
}

/**
 * Hides the panel and sets a flag in localStorage.
 */
function dismissInstructions() {
    if (instructionsPanel) {
        instructionsPanel.style.display = 'none';
    }
    // Set the flag so instructions don't show on future visits
    localStorage.setItem('instructionsDismissed', 'true');
}
// /**
//  * Replaces words in the text with clickable <span> elements and preserves paragraphs.
//  */
// function renderInteractiveText() {
//     // CRITICAL CHECK: Ensure germanText is loaded and not empty
//     if (!germanText || vocabularyData.length === 0) {
//         console.error("Text or vocabulary data is missing before rendering.");
//         return;
//     }

//     let textWithParagraphs = germanText;
    
//     // 1. Preserve paragraph breaks:
//     // Replace double line breaks (\n\s*\n - which handles blank lines) with </p><p>
//     textWithParagraphs = textWithParagraphs.trim()
//         .replace(/\n\s*\n/g, '</p><p>'); 

//     // 2. Wrap the entire body in initial/final paragraph tags
//     // This creates <p>Paragraph 1</p><p>Paragraph 2</p>...
//     textWithParagraphs = `<p>${textWithParagraphs}</p>`;


//     // 3. Now, proceed with word wrapping
//     vocabularyData.forEach(item => {
//         // Create a regular expression to find the whole word, ignoring case.
//         const regex = new RegExp(`\\b(${item.word})\\b`, 'gi');

//         // Replace the word with the clickable span
//         textWithParagraphs = textWithParagraphs.replace(regex, (match) => {
//             // Prevent double-wrapping 
//             if (match.startsWith('<span')) {
//                 return match; 
//             }
//             return `<span class="vocab-word" data-word="${item.word}">${match}</span>`;
//         });
//     });

//     // 4. Display the fully wrapped and paragraphed text in the HTML
//     textArea.innerHTML = textWithParagraphs;

//     // 5. Attach event listeners
//     document.querySelectorAll('.vocab-word').forEach(span => {
//         span.addEventListener('mouseover', handleWordHover);
//         span.addEventListener('click', handleWordClick); 
//     });
// }

/**
 * Replaces words in the text with clickable <span> elements and preserves paragraphs.
 * Includes a fix for German compound words/diacritics.
 */
function renderInteractiveText() {
    if (!germanText || vocabularyData.length === 0) {
        console.error("Text or vocabulary data is missing before rendering.");
        return;
    }
    
    let textWithParagraphs = germanText;
    
    // 1. Preserve paragraph breaks:
    textWithParagraphs = textWithParagraphs.trim()
        .replace(/\n\s*\n/g, '</p><p>'); 
    textWithParagraphs = `<p>${textWithParagraphs}</p>`;

    // 2. Proceed with word wrapping
    vocabularyData.forEach(item => {
        
        let regex;
        // Check if the word contains a German diacritic or compound part like 'ß' 
        // which can confuse the default \b word boundary.
        if (item.word.includes('ß') || item.word.includes('vater') || item.word.includes('mutter')) {
            // Use a look-around assertion for more reliable boundary checking
            // This pattern looks for the word followed by a non-letter/digit/space/HTML character.
            // This is safer than removing \b entirely.
            regex = new RegExp(`(?<![a-zA-ZäöüÄÖÜß])(${item.word})(?![a-zA-ZäöüÄÖÜß])`, 'gi');
        } else {
            // Use the standard, safer word boundary for most words
            regex = new RegExp(`\\b(${item.word})\\b`, 'gi');
        }

        // Replace the word with the clickable span
        textWithParagraphs = textWithParagraphs.replace(regex, (match) => {
            // CRITICAL: Prevent double-wrapping (which corrupts the HTML)
            if (match.startsWith('<span') || match.includes('<span')) {
                return `<span class="vocab-word" data-word="${item.word}">${match}</span>`; 
            }
            // Use a custom data attribute to store the word for easy lookup
            return `<span class="vocab-word" data-word="${item.word}">${match}</span>`;
        });
    });

    // 3. Display the text
    textArea.innerHTML = textWithParagraphs;

    // 4. Attach event listeners
    document.querySelectorAll('.vocab-word').forEach(span => {
        span.addEventListener('mouseover', handleWordHover);
        span.addEventListener('click', handleWordClick); 
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
            <button class="add-word-button" onclick="addWordToSet('${word}')">
                Wort zu Set hinzufügen (Add to Set)
            </button>
        `;
    }
}

/**
 * Handles the CLICK event on a vocabulary word to ADD it to the list.
 */
function handleWordClick(event) {
// 1. Get the word from the attribute, which contains the base form from JSON.
    const wordKey = event.target.dataset.word; 

    // 2. Normalize the word to lowercase to ensure it matches your JSON data.
    const word = wordKey.toLowerCase(); 
    
    // Find the full vocabulary entry from your main data source
    const vocabEntry = vocabularyData.find(v => v.word === word);

    // Check if the word is already selected (for toggling)
    const existingIndex = selectedVocab.findIndex(item => item.word === word);

    if (vocabEntry) {
        if (existingIndex === -1) {
            // Word is NOT selected, ADD it.
            selectedVocab.push({
                word: word,
                definition: vocabEntry.definition_german,    // <-- German definition (Required for sidebar display)
                definitionEN: vocabEntry.definition_english // <-- English definition (Required for CSV download)
            });
        } else {
            // Word IS selected, REMOVE it (toggle off).
            selectedVocab.splice(existingIndex, 1);
        }

        // Save and re-render the list after change
        saveAndRenderVocab(); 
    }
}

/**
 * The dedicated function called by the button to add the word to the list.
 */
function addWordToSet(word) {
    const vocabObject = vocabularyData.find(item => item.word === word);

    if (vocabObject) {
        // Check if the word is already in the selected list
        if (!selectedVocab.some(item => item.word === word)) {
            selectedVocab.push(vocabObject);
            saveAndRenderVocab();
            
            // Optional: Provide visual feedback on the button itself (or in the text)
            definitionDisplay.querySelector('.add-word-button').textContent = "Hinzugefügt! (Added!)";
            definitionDisplay.querySelector('.add-word-button').disabled = true;

        } else {
            alert(`"${word}" ist schon im Set! (Already in your set!)`);
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
        // Reset the definition display when the list is cleared/empty
        definitionDisplay.innerHTML = `
            Klicke oder fahre mit der Maus über ein 
            <span style="font-weight: bold;">fett gedrucktes</span> 
            Wort, um die Definition hier zu sehen.
        `;
        return;
    }

    selectedVocab.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
            <strong>${item.word}</strong>
            <p>DE: ${item.definition}</p>
            <p>EN: ${item.definitionEN}</p>
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
// 4. INITIALIZATION
// ========================================================================

// Add the event listener for the clear button
clearButton.addEventListener('click', clearVocabSet);

// Add the event listener for the chapter selector
chapterSelect.addEventListener('change', handleChapterChange);

// Start the entire process by loading the data
loadDataAndInitializeApp();

// ========================================================================
// 5. SUBMISSION HANDLER
// ========================================================================

// script.js (Submission Handler at the bottom of the file)

submissionForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const word = submitWordInput.value.trim();
    const definitionDE = document.getElementById('submit-definition').value.trim();
    const definitionEN = document.getElementById('submit-definition-en').value.trim();
    
    // Simple validation (now requires all three fields)
    if (!word || !definitionDE || !definitionEN) {
        submissionMessage.style.color = 'red';
        submissionMessage.textContent = "Bitte Wort, DE Definition, und EN Definition eingeben.";
        return;
    }
    
    if (typeof db === 'undefined') {
        submissionMessage.style.color = 'red';
        submissionMessage.textContent = "Fehler: Datenbank nicht verbunden.";
        return;
    }

    try {
        await submissionsCollection.add({
            word: word,
            definition_german: definitionDE, // Use the new variable name
            definition_english: definitionEN, // NEW: Save the English definition
            timestamp: firebase.firestore.FieldValue.serverTimestamp(),
            status: 'pending'
        });

        submissionMessage.style.color = 'green';
        submissionMessage.textContent = `Vielen Dank! Wort "${word}" wurde gesendet.`;
        
        // Clear the form after successful submission
        document.getElementById('submit-definition').value = '';
        document.getElementById('submit-definition-en').value = ''; // NEW: Clear English field
        submitWordInput.value = '';

    } catch (e) {
        // ... error handling remains the same ...
    }
});

// script.js (Event Listeners at the bottom of the file)

// Download button listener
if (downloadButton) {
    downloadButton.addEventListener('click', () => {
        const csvData = convertArrayToCSV(selectedVocab);
        if (csvData) {
            // Filename includes current date for easy reference
            const date = new Date().toISOString().slice(0, 10); 
            downloadCSV(csvData, `vocab_set_${date}.csv`);
        } else {
            alert('Dein Vokabel-Set ist leer!');
        }
    });
}


