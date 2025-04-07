// scripts/doc-linter.js
const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Check for HLD references in implementation code
const checkHLDReferences = (filePath) => {
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Only check for references in domain or service implementation files
  if (filePath.includes('domain') || filePath.includes('service')) {
    if (!content.includes('high-level-design.md')) {
      console.error(`ERROR: ${filePath} is missing reference to HLD`);
      return false;
    }
  }
  return true;
};

// Run on implementation files rather than LLD documents
glob.sync('src/**/*.{js,ts,py}')
  .forEach(checkHLDReferences);