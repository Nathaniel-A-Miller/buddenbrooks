// sync-vocab.js

/**
 * Reads the existing local JSON file for a chapter.
 * @param {number} chapterNum
 * @returns {Array<Object>} The existing vocabulary array, or an empty array if the file doesn't exist.
 */
function readExistingVocab(chapterNum) {
    const filename = path.join(OUTPUT_DIR, `vocab_ch${chapterNum}.json`);
    
    try {
        // Read the file synchronously
        const fileContent = fs.readFileSync(filename, 'utf8');
        // Parse and return the existing array
        return JSON.parse(fileContent); 
    } catch (error) {
        // If the file doesn't exist (E.g., new chapter), return an empty array
        if (error.code === 'ENOENT') {
            return [];
        }
        // Log other errors, but don't crash the entire job
        console.error(`Error reading existing vocab file ${filename}:`, error.message);
        return []; 
    }
}

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// --- CONFIGURATION ---
// The environment variable holding your secret key
const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT);
const COLLECTION_NAME = 'submissions';
const OUTPUT_DIR = 'vocab_data';
const MAX_CHAPTER = 97; // Define the total number of chapters

// --- INITIALIZATION ---
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    // Use your databaseURL from the Firebase config
    databaseURL: "https://buddenrbooks.firebaseio.com" 
  });
}
const db = admin.firestore();

/**
 * Ensures a number is zero-padded (e.g., 1 -> 01)
 * @param {number} num
 * @returns {string}
 */
const zeroPad = (num) => String(num).padStart(2, '0');

/**
 * Fetches all pending/approved submissions and organizes them by chapter.
 */
async function fetchAndOrganizeVocab() {
  console.log(`Fetching data from Firestore collection: ${COLLECTION_NAME}...`);
  
  // Fetch only approved submissions (assuming you have a 'status' field)
  const snapshot = await db.collection(COLLECTION_NAME)
    .where('status', '==', 'approved') 
    .get();

  const chapterData = new Array(MAX_CHAPTER + 1).fill(null).map(() => []);

  snapshot.forEach(doc => {
    const data = doc.data();
    
    // CRITICAL: Ensure your Firestore documents have a 'chapter' field that is a number
    const chapter = data.chapter; 

    if (chapter >= 1 && chapter <= MAX_CHAPTER) {
      // Structure the data to match your frontend JSON structure
      chapterData[chapter].push({
        word: data.word.toLowerCase(),
        definition_german: data.definition_german,
        definition_english: data.definition_english,
        chapter: chapter, // Keep the chapter number in the JSON for consistency
        // Add other necessary fields (like frequency, etc.)
      });
    }
  });

  return chapterData;
}


 * Writes the organized chapter data, merging with existing local files.
 * @param {Array<Array<Object>>} organizedData - New vocab fetched from Firebase
 */
function writeChapterFiles(organizedData) {
    // Ensure the output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR);
    }

    for (let i = 1; i <= MAX_CHAPTER; i++) {
        const newVocab = organizedData[i];
        
        // 1. READ EXISTING VOCAB
        const existingVocab = readExistingVocab(i);

        // 2. MERGE LOGIC (CRITICAL STEP)
        // Combine existing and new. We'll use a Map to keep track of unique words 
        // and ensure the new Firebase entry overrides the existing one (if needed).
        
        const mergedMap = new Map();
        
        // Add existing vocabulary first
        existingVocab.forEach(item => {
            mergedMap.set(item.word.toLowerCase(), item);
        });
        
        // Add new vocabulary, which will overwrite any duplicates from the existing list
        if (newVocab.length > 0) {
            newVocab.forEach(item => {
                mergedMap.set(item.word.toLowerCase(), item);
            });
        }
        
        // Convert the map back to an array
        const finalVocab = Array.from(mergedMap.values());
        
        // Check if anything has actually changed to prevent unnecessary commits (optimization)
        if (finalVocab.length === existingVocab.length && newVocab.length === 0) {
            console.log(`Skipping Chapter ${i}: No new approved vocabulary found.`);
            continue;
        }

        if (finalVocab.length === 0) {
            continue; // Skip writing an empty file
        }
        
        // 3. WRITE THE MERGED FILE
        const filename = path.join(OUTPUT_DIR, `vocab_ch${i}.json`);
        
        // Write the JSON file with pretty printing (2-space indent)
        fs.writeFileSync(filename, JSON.stringify(finalVocab, null, 2));
        console.log(`Successfully MERGED ${finalVocab.length} words (added ${newVocab.length} new) to ${filename}`);
    }
}

/**
 * Main execution function
 */
async function main() {
  try {
    const organizedVocab = await fetchAndOrganizeVocab();
    writeChapterFiles(organizedVocab);
    console.log("Vocabulary sync completed successfully!");
  } catch (error) {
    console.error("Sync process failed:", error);
    process.exit(1); // Exit with a failure code
  }
}

main();
