// sync-vocab.js

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

/**
 * Writes the organized chapter data to individual JSON files.
 * @param {Array<Array<Object>>} organizedData
 */
function writeChapterFiles(organizedData) {
  // Ensure the output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR);
  }

  for (let i = 1; i <= MAX_CHAPTER; i++) {
    const chapterVocab = organizedData[i];
    if (chapterVocab.length === 0) {
      console.log(`Skipping Chapter ${i}: No approved vocabulary found.`);
      continue;
    }
    
    // NOTE: If your files are NOT zero-padded (vocab_ch1.json), change the next line
    const paddedChapter = i; // CHANGE TO: const paddedChapter = zeroPad(i); 

    const filename = path.join(OUTPUT_DIR, `vocab_ch${paddedChapter}.json`);
    
    // Write the JSON file with pretty printing (2-space indent)
    fs.writeFileSync(filename, JSON.stringify(chapterVocab, null, 2));
    console.log(`Successfully wrote ${chapterVocab.length} words to ${filename}`);
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
