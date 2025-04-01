// scripts/doc-linter.js
const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Check for HLD references in LLD documents
const checkHLDReferences = (filePath) => {
  const content = fs.readFileSync(filePath, 'utf8');
  if (!content.includes('high-level-design.md')) {
    console.error(`ERROR: ${filePath} is missing reference to HLD`);
    return false;
  }
  return true;
};

// Run on all LLD documents
glob.sync('docs/architecture/low-level-design/**/*.md')
  .forEach(checkHLDReferences);