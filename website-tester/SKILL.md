---
name: website-tester
description: End-to-end functional testing for web apps — fills forms, clicks buttons, verifies CRUD. Use for "test my website", "test all the forms", or "functional test my app".
---

# Website Functional Tester

Automated end-to-end testing that actually exercises your web application — fills forms, submits data, clicks buttons, and verifies CRUD operations work.

## What It Does

Unlike smoke tests that just check if elements exist, this tool:

1. **Fills forms with realistic test data** — emails, passwords, names, dates, etc.
2. **Submits forms and checks results** — verifies success/error messages
3. **Tests CRUD workflows** — Create, Read, Update, Delete operations
4. **Clicks buttons and verifies effects** — checks for page changes, navigation, errors
5. **Crawls all pages** — discovers and tests every page on your site

## CRUD Detection

The tester automatically identifies operation types by analyzing button/form text:

| Operation | Detected Keywords |
|-----------|-------------------|
| **Create** | add, create, new, register, sign up, submit, post |
| **Update** | edit, update, modify, change, save, apply |
| **Delete** | delete, remove, trash, discard, cancel, clear |
| **Read** | view, show, details, open, get |

## Usage

### Full Functional Test

```bash
cd /path/to/skill
pip install playwright
playwright install chromium

# Test all pages, fill all forms, submit everything
python scripts/test_website.py https://your-app.herokuapp.com
```

### With Report

```bash
python scripts/test_website.py https://your-app.herokuapp.com \
    --output report.json \
    --screenshots-dir ./screenshots
```

### Including Delete Operations

By default, delete operations are **skipped** to avoid data loss. Enable with:

```bash
python scripts/test_website.py https://your-app.herokuapp.com --test-destructive
```

### Quick Smoke Test

```bash
# Test only first 5 pages
python scripts/test_website.py https://your-app.herokuapp.com --max-pages 5
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--output`, `-o` | Save JSON report to file | None |
| `--screenshots-dir`, `-s` | Directory for failure screenshots | None |
| `--max-pages` | Maximum pages to crawl (0 = unlimited) | 0 (all) |
| `--timeout` | Page load timeout (ms) | 15000 |
| `--test-destructive` | Also test delete operations | False |
| `--quiet`, `-q` | Suppress console output | False |

## Test Data

Forms are filled with appropriate test data based on field type:

| Field Type | Test Value |
|------------|------------|
| email | test@example.com |
| password | TestPass123! |
| text | Test Value |
| number | 42 |
| tel | 555-123-4567 |
| url | https://example.com |
| textarea | This is test content... |
| date | 2025-01-15 |
| time | 14:30 |
| color | #ff5500 |

Field names/placeholders are analyzed to pick better values (e.g., "name" field gets "Test User").

## Output

### Console Progress

```
Functional Testing: https://your-app.herokuapp.com
Max pages: unlimited
Test destructive ops: False
======================================================================

[1] Testing: https://your-app.herokuapp.com (0 queued)
    Elements: 12 | Forms: 2 | ✓ 18 | ✗ 1
      Testing form: create (4 fields)

[2] Testing: https://your-app.herokuapp.com/items (3 queued)
    Elements: 8 | Forms: 1 | ✓ 12 | ✗ 0
      Testing form: update (3 fields)
```

### Summary Report

```
======================================================================
WEBSITE FUNCTIONAL TEST REPORT
======================================================================
URL: https://your-app.herokuapp.com
Pages tested:     15
Elements found:   87
Forms tested:     12
Workflows tested: 8
----------------------------------------------------------------------
Tests passed: 142
Tests failed: 3
Pass rate:    97.9%
----------------------------------------------------------------------

CRUD Operations Detected:
  Create: 4
  Update: 6
  Delete: 2

WORKFLOWS TESTED
======================================================================
1. Form create: 4 fields
   https://your-app.herokuapp.com/items/new
2. Form update: 3 fields
   https://your-app.herokuapp.com/items/1/edit
```

## Interpreting Results

### Success Indicators
The tester looks for these patterns after form submission:
- "success", "saved", "created", "updated", "deleted"
- "added", "submitted", "complete", "done", "thank you"

### Error Indicators
These trigger a test failure:
- "error", "failed", "invalid", "required", "missing"
- "incorrect", "wrong", "problem", "unable"

## Limitations

- **No authentication** — tests public pages only (see Extending below)
- **No file uploads** — file inputs are detected but not tested with actual files
- **Delete ops skipped by default** — use `--test-destructive` to enable
- **Single domain** — only tests pages within the same domain
- **No JS framework state** — may miss some React/Vue state changes

## Extending

### Adding Authentication

Modify the `run()` method in `test_website.py`:

```python
async def run(self, verbose: bool = False) -> FullReport:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(...)
        
        # Login first
        page = await context.new_page()
        await page.goto("https://your-app.com/login")
        await page.fill('input[name="email"]', "test@example.com")
        await page.fill('input[name="password"]', "yourpassword")
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/dashboard**")
        await page.close()
        
        # Continue with testing (auth cookies are preserved)
        ...
```

### Custom Test Data

Modify the `TEST_DATA` dict at the top of the script to use your own test values.

## Tips

1. **Start without `--test-destructive`** to avoid deleting real data
2. **Use a staging environment** for full testing including deletes
3. **Check the JSON report** for detailed per-element results
4. **Add `data-testid` attributes** to your HTML for more reliable selectors
5. **Watch for false positives** — some apps show "error" text that isn't an actual error
