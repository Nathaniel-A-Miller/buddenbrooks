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
// 1. DATA FILE PATHS
// ========================================================================
const TEXT_FILE_PATH = 'text.txt';
const VOCAB_FILE_PATH = 'vocab.json';


// ========================================================================
// 2. DOM ELEMENTS & GLOBAL VARIABLES
// ========================================================================

const textArea = document.getElementById('german-text-area');
const vocabList = document.getElementById('selected-vocab-list');
const vocabCountSpan = document.getElementById('vocab-count');
const clearButton = document.getElementById('clear-vocab-button');
const definitionDisplay = document.getElementById('definition-display'); // New element

// NEW VARIABLES
const submissionForm = document.getElementById('submission-form');
const submitWordInput = document.getElementById('submit-word');
const submissionMessage = document.getElementById('submission-message');
const submitDefinitionEnInput = document.getElementById('submit-definition-en');

let germanText = '';
let vocabularyData = [];
// Load selected words from the browser's local storage or start with an empty array
let selectedVocab = JSON.parse(localStorage.getItem('selectedVocab')) || [];


// ========================================================================
// 3. CORE FUNCTIONS
// ========================================================================

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
                return match; 
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
// 4. INITIALIZATION
// ========================================================================

// Add the event listener for the clear button
clearButton.addEventListener('click', clearVocabSet);

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
