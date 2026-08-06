#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

const MARKDOWN_LINK_REGEX = /\[([^\]]*)\]\(([^)]+)\)/g;

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function extractHeadings(content) {
  const headings = [];
  const contentWithoutCode = content.replace(/```[\s\S]*?```/g, '');
  const headingRegex = /^#{1,6}\s+(.+)$/gm;
  let match;
  while ((match = headingRegex.exec(contentWithoutCode)) !== null) {
    const title = match[1].replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').trim();
    headings.push(slugify(title));
  }
  return new Set(headings);
}

function walkMdFiles(dir) {
  const results = [];
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return results;
  }
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
        results.push(...walkMdFiles(fullPath));
      }
    } else if (entry.name.endsWith('.md')) {
      results.push(fullPath);
    }
  }
  return results;
}

function isInsideInlineCode(rawContent, position) {
  // Check if position is inside inline backtick code by counting
  // unpaired backticks before this position in the RAW content.
  // An odd count means we're inside inline code.
  const before = rawContent.slice(0, position);
  // Don't count backticks inside fenced code blocks
  const noFenced = before.replace(/```[\s\S]*?```/g, '');
  const backtickCount = (noFenced.match(/`/g) || []).length;
  return backtickCount % 2 === 1;
}

function extractLinks(content, filePath) {
  const links = [];
  // Strip fenced code blocks (``` ... ```) so links inside them aren't checked
  const contentWithoutCode = content.replace(/```[\s\S]*?```/g, (m) =>
    m.replace(/[^\n]/g, ' ')
  );

  let match;
  while ((match = MARKDOWN_LINK_REGEX.exec(contentWithoutCode)) !== null) {
    const url = match[2].trim();
    const before = contentWithoutCode.slice(0, match.index);
    const lineNumber = before.split('\n').length;
    // Skip links inside inline backtick code (syntax examples, not real links)
    if (isInsideInlineCode(content, match.index)) {
      continue;
    }
    links.push({ url, lineNumber });
  }

  return links;
}

function resolveTarget(linkPath, sourceFile) {
  if (linkPath.startsWith('/')) {
    return path.join(ROOT, linkPath);
  }
  return path.resolve(path.dirname(sourceFile), linkPath);
}

function validateLink(link, sourceFile, allMdFiles, headingsMap) {
  const { url } = link;

  if (url.startsWith('http://') || url.startsWith('https://')) return null;
  if (url.startsWith('mailto:') || url.startsWith('tel:') || url.startsWith('javascript:') || url.startsWith('data:')) return null;

  if (url.startsWith('#')) {
    const slug = url.slice(1);
    const fileHeadings = headingsMap.get(sourceFile);
    if (fileHeadings && slug && !fileHeadings.has(slug)) {
      return `Anchor "#${slug}" not found in current file`;
    }
    return null;
  }

  const [linkPath, anchor] = url.split('#');
  if (!linkPath) return null;

  if (!linkPath.endsWith('.md')) return null;

  const resolved = path.normalize(resolveTarget(linkPath, sourceFile));
  const relative = path.relative(ROOT, resolved);

  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    return `Target "${url}" resolves outside repo root`;
  }

  if (!fs.existsSync(resolved)) {
    return `File not found: "${path.normalize(linkPath)}" (resolved to "${relative}")`;
  }

  if (anchor) {
    const resolvedSlug = slugify(decodeURIComponent(anchor));
    const targetHeadings = headingsMap.get(resolved);
    const altResolvedSlug = slugify(anchor);
    if (targetHeadings && !targetHeadings.has(resolvedSlug) && !targetHeadings.has(altResolvedSlug)) {
      return `Anchor "#${anchor}" not found in "${relative}"`;
    }
  }

  return null;
}

function main() {
  const args = process.argv.slice(2);
  const CHECK_ANCHORS = args.includes('--check-anchors');

  const allMdFiles = walkMdFiles(ROOT);
  console.log(`Found ${allMdFiles.length} .md files\n`);

  const headingsMap = new Map();
  for (const file of allMdFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    headingsMap.set(file, extractHeadings(content));
  }

  let totalLinks = 0;
  let totalBroken = 0;
  const errors = [];

  for (const file of allMdFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const links = extractLinks(content, file);

    const fileErrors = [];
    for (const link of links) {
      totalLinks++;
      if (!CHECK_ANCHORS && link.url.startsWith('#')) {
        continue;
      }
      const error = validateLink(link, file, allMdFiles, headingsMap);
      if (error) {
        fileErrors.push({ line: link.lineNumber, url: link.url, error });
      }
    }

    if (fileErrors.length > 0) {
      errors.push({ file: path.relative(ROOT, file), errors: fileErrors });
      totalBroken += fileErrors.length;
    }
  }

  console.log(`Links checked: ${totalLinks}`);
  console.log(`Broken links: ${totalBroken}\n`);

  if (errors.length === 0) {
    console.log('No broken links found');
    process.exit(0);
  }

  for (const { file, errors: fileErrors } of errors) {
    console.log(`\n${file}`);
    for (const { line, url, error } of fileErrors) {
      console.log(`  Line ${line}: ${url}`);
      console.log(`    ${error}`);
    }
  }

  console.log(`\nFound ${totalBroken} broken link(s) in ${errors.length} file(s)`);
  process.exit(1);
}

main();
