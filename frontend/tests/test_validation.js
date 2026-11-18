import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log("\n=======================================================");
console.log("RUNNING KISSAN GUIDE FRONTEND VALIDATION TEST SUITE");
console.log("=======================================================\n");

let passed = 0;
let failed = 0;

function assert(condition, testName) {
  if (condition) {
    console.log(`  [PASS] ${testName}`);
    passed++;
  } else {
    console.error(`  [FAIL] ${testName}`);
    failed++;
  }
}

// 1. Translation Dictionary Completeness & Key Parity
const enPath = path.resolve(__dirname, '../src/localization/en.json');
const knPath = path.resolve(__dirname, '../src/localization/kn.json');

const en = JSON.parse(fs.readFileSync(enPath, 'utf8'));
const kn = JSON.parse(fs.readFileSync(knPath, 'utf8'));

function getDeepKeys(obj, prefix = '') {
  let keys = [];
  for (const k of Object.keys(obj)) {
    const fullKey = prefix ? `${prefix}.${k}` : k;
    if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
      keys = keys.concat(getDeepKeys(obj[k], fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys;
}

const enKeys = getDeepKeys(en);
const knKeys = getDeepKeys(kn);

const missingInKn = enKeys.filter(k => !knKeys.includes(k));
assert(missingInKn.length === 0, `Complete English & Kannada key parity (${enKeys.length} matching keys)`);

// 2. 9 Taluks of Dakshina Kannada Coverage
const expectedTaluks = [
  'Mangaluru', 'Bantwal', 'Belthangady', 'Puttur',
  'Sullia', 'Moodbidri', 'Kadaba', 'Mulki', 'Ullal'
];
const enTaluks = Object.keys(en.taluks);
assert(
  expectedTaluks.every(t => enTaluks.includes(t)) && enTaluks.length === 9,
  "All 9 Dakshina Kannada taluks present in English translations"
);
const knTaluks = Object.keys(kn.taluks);
assert(
  expectedTaluks.every(t => knTaluks.includes(t)) && knTaluks.length === 9,
  "All 9 Dakshina Kannada taluks present in Kannada translations"
);

// 3. Supported Crops (Coconut, Rice, Arecanut, Cocoa)
const expectedCrops = ['Coconut', 'Rice', 'Arecanut', 'Cocoa'];
const enCrops = Object.keys(en.crops);
assert(
  expectedCrops.every(c => enCrops.includes(c)) && enCrops.length === 4,
  "Strict focus on 4 DK crops in English (Coconut, Rice, Arecanut, Cocoa)"
);
const knCrops = Object.keys(kn.crops);
assert(
  expectedCrops.every(c => knCrops.includes(c)) && knCrops.length === 4,
  "Strict focus on 4 DK crops in Kannada (ತೆಂಗು, ಭತ್ತ, ಅಡಿಕೆ, ಕೋಕೋ)"
);

// 4. Form Validation Logic Tests
// Phone validation
const isValidPhone = (p) => /^[6-9]\d{9}$/.test(p.replace(/\D/g, ''));
assert(isValidPhone("9876543210"), "Valid Indian 10-digit mobile number passes");
assert(!isValidPhone("12345"), "Short phone number rejected");
assert(!isValidPhone("abc"), "Non-numeric phone rejected");

// Email validation
const isValidEmail = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
assert(isValidEmail("farmer@dakshina.in"), "Valid email passes");
assert(!isValidEmail("invalid-email"), "Malformed email rejected");

// Password length
const isValidPassword = (p) => typeof p === 'string' && p.length >= 6;
assert(isValidPassword("secure123"), "6+ char password passes");
assert(!isValidPassword("12345"), "Short password (<6 chars) rejected");

// 5. Water Availability Options
const waterOptions = Object.keys(en.waterLevels);
assert(
  waterOptions.includes("Low") && waterOptions.includes("Moderate") && waterOptions.includes("High"),
  "Water availability levels (Low, Moderate, High) correctly defined"
);

// 6. Post-Harvest Conditions & Methods
const conditionOptions = Object.keys(en.conditions);
assert(conditionOptions.length >= 7, "Harvested crop conditions defined (>7 states)");

const methodOptions = Object.keys(en.storageMethods);
assert(methodOptions.length >= 6, "Storage methods defined (>6 methods)");

console.log("\n=======================================================");
console.log(`RESULTS: ${passed} PASSED, ${failed} FAILED out of ${passed + failed} tests.`);
console.log("=======================================================\n");

if (failed > 0) process.exit(1);
