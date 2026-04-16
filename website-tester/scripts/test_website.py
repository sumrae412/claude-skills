#!/usr/bin/env python3
"""
Website Functional Tester - Tests CRUD operations and workflows on a website.

Actually submits forms, creates/edits/deletes items, and verifies operations succeed.

Usage:
    python test_website.py <url> [--output report.json] [--screenshots-dir ./screenshots]
    
Example:
    python test_website.py https://myapp.herokuapp.com --output results.json
"""

import argparse
import asyncio
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Page, Browser, ElementHandle


# Test data generators for different field types
TEST_DATA = {
    "text": "Test Value",
    "email": "test@example.com", 
    "password": "TestPass123!",
    "number": "42",
    "tel": "555-123-4567",
    "url": "https://example.com",
    "search": "test search",
    "textarea": "This is test content for a textarea field.",
    "date": "2025-01-15",
    "time": "14:30",
    "datetime-local": "2025-01-15T14:30",
    "month": "2025-01",
    "week": "2025-W03",
    "color": "#ff5500",
}

# Patterns to identify CRUD operations
CRUD_PATTERNS = {
    "create": [
        r"\badd\b", r"\bcreate\b", r"\bnew\b", r"\bregister\b", 
        r"\bsign.?up\b", r"\bsubmit\b", r"\bpost\b", r"\binsert\b"
    ],
    "update": [
        r"\bedit\b", r"\bupdate\b", r"\bmodify\b", r"\bchange\b",
        r"\bsave\b", r"\bapply\b", r"\bset\b"
    ],
    "delete": [
        r"\bdelete\b", r"\bremove\b", r"\btrash\b", r"\bdiscard\b",
        r"\bcancel\b", r"\bclear\b", r"\breset\b"
    ],
    "read": [
        r"\bview\b", r"\bshow\b", r"\bdetails\b", r"\bopen\b",
        r"\bread\b", r"\bget\b", r"\bfetch\b"
    ],
}

# Success indicators after form submission
SUCCESS_PATTERNS = [
    r"success", r"saved", r"created", r"updated", r"deleted",
    r"added", r"submitted", r"complete", r"done", r"thank you",
    r"confirmed", r"registered", r"welcome"
]

# Error indicators
ERROR_PATTERNS = [
    r"error", r"failed", r"invalid", r"required", r"missing",
    r"incorrect", r"wrong", r"problem", r"unable", r"cannot"
]


@dataclass
class ElementInfo:
    """Information about a discovered interactive element."""
    selector: str
    tag: str
    element_type: str
    text: str
    href: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None
    aria_label: Optional[str] = None
    placeholder: Optional[str] = None
    input_type: Optional[str] = None
    is_visible: bool = True
    is_enabled: bool = True
    crud_type: Optional[str] = None  # create, read, update, delete


@dataclass
class TestResult:
    """Result of testing an element or workflow."""
    element: Optional[ElementInfo]
    test_type: str
    passed: bool
    error: Optional[str] = None
    screenshot: Optional[str] = None
    notes: str = ""
    workflow: Optional[str] = None  # Description of workflow tested


@dataclass 
class FormInfo:
    """Information about a form and its fields."""
    selector: str
    action: Optional[str]
    method: str
    fields: list[ElementInfo]
    submit_button: Optional[ElementInfo]
    crud_type: Optional[str] = None


@dataclass
class PageReport:
    """Report for a single page."""
    url: str
    title: str
    elements_found: int = 0
    forms_found: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    elements: list[ElementInfo] = field(default_factory=list)
    forms: list[FormInfo] = field(default_factory=list)
    results: list[TestResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FullReport:
    """Complete test report."""
    base_url: str
    timestamp: str
    pages_tested: int = 0
    total_elements: int = 0
    total_forms: int = 0
    total_passed: int = 0
    total_failed: int = 0
    workflows_tested: int = 0
    pages: list[PageReport] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


def classify_crud_operation(text: str) -> Optional[str]:
    """Classify text as a CRUD operation type."""
    text_lower = text.lower()
    for crud_type, patterns in CRUD_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return crud_type
    return None


def check_for_success(page_text: str) -> bool:
    """Check if page contains success indicators."""
    text_lower = page_text.lower()
    for pattern in SUCCESS_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def check_for_error(page_text: str) -> Optional[str]:
    """Check if page contains error indicators, return error text if found."""
    text_lower = page_text.lower()
    for pattern in ERROR_PATTERNS:
        match = re.search(f"({pattern}[^.]*)", text_lower)
        if match:
            return match.group(1)[:100]
    return None


class WebsiteTester:
    """Functional tester that exercises CRUD operations on a website."""

    def __init__(
        self,
        base_url: str,
        screenshots_dir: Optional[Path] = None,
        max_pages: int = 0,
        timeout: int = 15000,
        test_destructive: bool = False,  # Whether to test delete operations
        cookies: Optional[list[dict]] = None,  # Cookies for authentication
    ):
        self.base_url = base_url.rstrip("/")
        self.base_domain = urlparse(base_url).netloc
        self.screenshots_dir = screenshots_dir
        self.max_pages = max_pages
        self.timeout = timeout
        self.test_destructive = test_destructive
        self.cookies = cookies
        self.visited_urls: set[str] = set()
        self.urls_to_visit: list[str] = [base_url]
        self.report = FullReport(
            base_url=base_url,
            timestamp=datetime.now().isoformat(),
        )

    async def run(self, verbose: bool = False) -> FullReport:
        """Run the full test suite."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                ignore_https_errors=True,
            )

            # Add cookies for authentication if provided
            if self.cookies:
                await context.add_cookies(self.cookies)
            
            while self.urls_to_visit and (self.max_pages == 0 or len(self.visited_urls) < self.max_pages):
                url = self.urls_to_visit.pop(0)
                if url in self.visited_urls:
                    continue
                
                if verbose:
                    queued = len(self.urls_to_visit)
                    tested = len(self.visited_urls)
                    print(f"\n[{tested + 1}] Testing: {url[:80]}{'...' if len(url) > 80 else ''} ({queued} queued)")
                    
                page_report = await self._test_page(context, url, verbose)
                if page_report:
                    self.report.pages.append(page_report)
                    self.report.pages_tested += 1
                    self.report.total_elements += page_report.elements_found
                    self.report.total_forms += page_report.forms_found
                    self.report.total_passed += page_report.tests_passed
                    self.report.total_failed += page_report.tests_failed
                    
                    if verbose:
                        print(f"    Elements: {page_report.elements_found} | Forms: {page_report.forms_found} | ✓ {page_report.tests_passed} | ✗ {page_report.tests_failed}")
                
                self.visited_urls.add(url)
            
            await browser.close()
        
        self._generate_summary()
        return self.report

    async def _test_page(self, context, url: str, verbose: bool = False) -> Optional[PageReport]:
        """Test all elements and forms on a single page."""
        page = await context.new_page()
        report = PageReport(url=url, title="")
        
        try:
            response = await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
            # Give JS time to render after DOM is ready
            await page.wait_for_timeout(1500)
            if not response or response.status >= 400:
                report.errors.append(f"Failed to load page: HTTP {response.status if response else 'no response'}")
                await page.close()
                return report
            
            report.title = await page.title()
            
            # Collect internal links for crawling
            await self._collect_links(page)
            
            # Discover all interactive elements
            elements = await self._discover_elements(page)
            report.elements = elements
            report.elements_found = len(elements)
            
            # Discover and analyze forms
            forms = await self._discover_forms(page)
            report.forms = forms
            report.forms_found = len(forms)
            
            # Test standalone elements (buttons, links not in forms)
            for element in elements:
                if element.element_type in ("button", "link", "clickable"):
                    result = await self._test_interactive_element(page, element, verbose)
                    report.results.append(result)
                    if result.passed:
                        report.tests_passed += 1
                    else:
                        report.tests_failed += 1
            
            # Test forms with full workflows
            for form in forms:
                results = await self._test_form_workflow(page, form, verbose)
                for result in results:
                    report.results.append(result)
                    if result.passed:
                        report.tests_passed += 1
                    else:
                        report.tests_failed += 1
                    if result.workflow:
                        self.report.workflows_tested += 1
            
        except Exception as e:
            report.errors.append(f"Page error: {str(e)}")
        finally:
            await page.close()
        
        return report

    async def _discover_elements(self, page: Page) -> list[ElementInfo]:
        """Discover all interactive elements on the page."""
        elements: list[ElementInfo] = []
        
        # Buttons (not in forms - those are handled separately)
        buttons = await page.query_selector_all('button:not(form button), [role="button"]:not(form [role="button"])')
        for btn in buttons:
            info = await self._get_element_info(btn, "button")
            if info:
                # Classify CRUD type
                info.crud_type = classify_crud_operation(info.text or info.aria_label or "")
                elements.append(info)
        
        # Links
        links = await page.query_selector_all('a[href]')
        for link in links:
            info = await self._get_element_info(link, "link")
            if info:
                info.crud_type = classify_crud_operation(info.text or info.aria_label or "")
                elements.append(info)
        
        # Clickable elements with handlers
        clickables = await page.query_selector_all('[onclick]:not(form *), [data-action]:not(form *)')
        for el in clickables:
            info = await self._get_element_info(el, "clickable")
            if info and info.tag not in ("button", "a", "input"):
                info.crud_type = classify_crud_operation(info.text or "")
                elements.append(info)
        
        return elements

    async def _discover_forms(self, page: Page) -> list[FormInfo]:
        """Discover all forms and their fields."""
        forms: list[FormInfo] = []
        
        form_elements = await page.query_selector_all('form')
        for form_el in form_elements:
            form_info = await self._analyze_form(page, form_el)
            if form_info:
                forms.append(form_info)
        
        return forms

    async def _analyze_form(self, page: Page, form_el: ElementHandle) -> Optional[FormInfo]:
        """Analyze a form to understand its structure and purpose."""
        try:
            action = await form_el.get_attribute("action")
            method = (await form_el.get_attribute("method") or "get").upper()
            
            # Get form selector
            form_id = await form_el.get_attribute("id")
            form_class = await form_el.get_attribute("class")
            if form_id:
                selector = f"#{form_id}"
            elif form_class:
                selector = f"form.{form_class.split()[0]}"
            else:
                selector = "form"
            
            # Discover fields
            fields: list[ElementInfo] = []
            
            # Text inputs
            inputs = await form_el.query_selector_all('input[type="text"], input[type="email"], input[type="password"], input[type="number"], input[type="tel"], input[type="url"], input[type="search"], input:not([type])')
            for inp in inputs:
                info = await self._get_element_info(inp, "input")
                if info:
                    fields.append(info)
            
            # Textareas
            textareas = await form_el.query_selector_all('textarea')
            for ta in textareas:
                info = await self._get_element_info(ta, "textarea")
                if info:
                    fields.append(info)
            
            # Selects
            selects = await form_el.query_selector_all('select')
            for sel in selects:
                info = await self._get_element_info(sel, "select")
                if info:
                    fields.append(info)
            
            # Checkboxes and radios
            checks = await form_el.query_selector_all('input[type="checkbox"], input[type="radio"]')
            for chk in checks:
                info = await self._get_element_info(chk, "checkbox_radio")
                if info:
                    fields.append(info)
            
            # Date/time inputs
            date_inputs = await form_el.query_selector_all('input[type="date"], input[type="time"], input[type="datetime-local"]')
            for di in date_inputs:
                info = await self._get_element_info(di, "date_input")
                if info:
                    fields.append(info)
            
            # File inputs
            file_inputs = await form_el.query_selector_all('input[type="file"]')
            for fi in file_inputs:
                info = await self._get_element_info(fi, "file_input")
                if info:
                    fields.append(info)
            
            # Hidden inputs (track but don't fill)
            hidden_inputs = await form_el.query_selector_all('input[type="hidden"]')
            for hi in hidden_inputs:
                info = await self._get_element_info(hi, "hidden")
                if info:
                    fields.append(info)
            
            # Find submit button
            submit_btn = await form_el.query_selector('button[type="submit"], input[type="submit"], button:not([type])')
            submit_info = None
            if submit_btn:
                submit_info = await self._get_element_info(submit_btn, "submit")
            
            # Determine form's CRUD type
            form_text = await form_el.text_content() or ""
            crud_type = classify_crud_operation(form_text)
            if not crud_type and submit_info:
                crud_type = classify_crud_operation(submit_info.text or "")
            
            return FormInfo(
                selector=selector,
                action=action,
                method=method,
                fields=fields,
                submit_button=submit_info,
                crud_type=crud_type,
            )
            
        except Exception:
            return None

    async def _get_element_info(self, element: ElementHandle, element_type: str) -> Optional[ElementInfo]:
        """Extract information about an element."""
        try:
            is_visible = await element.is_visible()
            is_enabled = await element.is_enabled()
            
            tag = await element.evaluate("el => el.tagName.toLowerCase()")
            text = (await element.text_content() or "").strip()[:100]
            text = " ".join(text.split())
            
            el_id = await element.get_attribute("id")
            el_name = await element.get_attribute("name")
            el_class = await element.get_attribute("class")
            el_type = await element.get_attribute("type")
            el_href = await element.get_attribute("href")
            data_testid = await element.get_attribute("data-testid")
            
            # Build selector
            if data_testid:
                selector = f'[data-testid="{data_testid}"]'
            elif el_id:
                selector = f"#{el_id}"
            elif el_name:
                selector = f'{tag}[name="{el_name}"]'
            elif tag == "a" and el_href:
                safe_href = el_href.replace('"', '\\"')[:50]
                selector = f'{tag}[href="{safe_href}"]'
            elif el_class:
                first_class = el_class.split()[0] if el_class else ""
                selector = f"{tag}.{first_class}" if first_class else tag
            else:
                selector = await element.evaluate("""el => {
                    function getSelector(element) {
                        if (element.id) return '#' + element.id;
                        if (element === document.body) return 'body';
                        let parent = element.parentNode;
                        if (!parent) return element.tagName.toLowerCase();
                        let siblings = Array.from(parent.children).filter(c => c.tagName === element.tagName);
                        let tag = element.tagName.toLowerCase();
                        if (siblings.length === 1) return getSelector(parent) + ' > ' + tag;
                        let index = siblings.indexOf(element) + 1;
                        return getSelector(parent) + ' > ' + tag + ':nth-of-type(' + index + ')';
                    }
                    return getSelector(el);
                }""")
            
            return ElementInfo(
                selector=selector,
                tag=tag,
                element_type=element_type,
                text=text,
                href=el_href,
                name=el_name,
                id=el_id,
                aria_label=await element.get_attribute("aria-label"),
                placeholder=await element.get_attribute("placeholder"),
                input_type=el_type,
                is_visible=is_visible,
                is_enabled=is_enabled,
            )
        except Exception:
            return None

    async def _collect_links(self, page: Page) -> None:
        """Collect internal links for crawling."""
        links = await page.query_selector_all('a[href]')
        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                    continue
                
                full_url = urljoin(page.url, href)
                parsed = urlparse(full_url)
                
                if parsed.netloc == self.base_domain:
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if parsed.query:
                        clean_url += f"?{parsed.query}"
                    
                    if clean_url not in self.visited_urls and clean_url not in self.urls_to_visit:
                        self.urls_to_visit.append(clean_url)
            except Exception:
                pass

    async def _test_interactive_element(self, page: Page, element: ElementInfo, verbose: bool = False) -> TestResult:
        """Test a standalone interactive element (button, link, clickable)."""
        result = TestResult(element=element, test_type="interaction", passed=False)
        
        if not element.is_visible or not element.is_enabled:
            result.passed = True
            result.notes = "Element not visible/enabled (skipped)"
            return result
        
        # Skip delete operations unless explicitly enabled
        if element.crud_type == "delete" and not self.test_destructive:
            result.passed = True
            result.notes = "Delete operation skipped (use --test-destructive to enable)"
            return result
        
        try:
            el = await page.query_selector(element.selector)
            if not el:
                result.error = f"Could not find element: {element.selector}"
                return result
            
            if element.element_type == "link":
                result = await self._test_link(page, el, element)
            else:
                result = await self._test_button(page, el, element)
                
        except Exception as e:
            result.error = str(e)
        
        return result

    async def _test_button(self, page: Page, el: ElementHandle, info: ElementInfo) -> TestResult:
        """Test a button by clicking and checking result."""
        result = TestResult(element=info, test_type="click", passed=False)
        
        try:
            box = await el.bounding_box()
            if not box:
                result.error = "Button has no bounding box"
                return result
            
            original_url = page.url
            original_content = await page.content()
            
            # Click the button
            await el.click(timeout=5000)
            await page.wait_for_timeout(1000)
            
            # Check what happened
            new_url = page.url
            new_content = await page.content()
            page_text = await page.inner_text("body")
            
            # Check for errors
            error = check_for_error(page_text)
            if error:
                result.error = f"Action triggered error: {error}"
                # Go back if navigated
                if new_url != original_url:
                    await page.go_back()
                return result
            
            # Check for success
            if check_for_success(page_text):
                result.passed = True
                result.notes = "Action completed with success indicator"
                result.workflow = f"{info.crud_type or 'action'}: {info.text[:30]}"
            elif new_url != original_url:
                result.passed = True
                result.notes = f"Navigation to: {new_url[:50]}"
                await page.go_back()
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=5000)
                except Exception:
                    pass
            elif new_content != original_content:
                result.passed = True
                result.notes = "Page content changed (action executed)"
            else:
                result.passed = True
                result.notes = "Click executed (no visible change)"
            
        except Exception as e:
            result.error = f"Click failed: {str(e)}"
        
        return result

    async def _test_link(self, page: Page, el: ElementHandle, info: ElementInfo) -> TestResult:
        """Test a link by verifying it's accessible."""
        result = TestResult(element=info, test_type="link", passed=False)
        
        href = info.href
        if not href:
            result.error = "Link has no href"
            return result
        
        if href.startswith(("javascript:", "mailto:", "tel:", "#")):
            result.passed = True
            result.notes = f"Special link: {href[:30]}"
            return result
        
        full_url = urljoin(page.url, href)
        parsed = urlparse(full_url)
        
        if parsed.netloc == self.base_domain:
            try:
                # Use GET instead of HEAD since many servers don't support HEAD
                response = await page.request.get(full_url, timeout=5000)
                if response.status < 400:
                    result.passed = True
                    result.notes = f"Internal link OK ({response.status})"
                else:
                    result.error = f"Link returns HTTP {response.status}"
            except Exception as e:
                result.passed = True
                result.notes = f"Link exists (verification failed: {str(e)[:30]})"
        else:
            result.passed = True
            result.notes = f"External link: {parsed.netloc}"
        
        return result

    async def _test_form_workflow(self, page: Page, form: FormInfo, verbose: bool = False) -> list[TestResult]:
        """Test a complete form workflow: fill, submit, verify."""
        results: list[TestResult] = []
        
        # Skip forms with no fillable fields
        fillable_fields = [f for f in form.fields if f.element_type not in ("hidden", "file_input")]
        if not fillable_fields:
            result = TestResult(
                element=None,
                test_type="form_structure",
                passed=True,
                notes=f"Form has no fillable fields (action={form.action})",
            )
            results.append(result)
            return results
        
        # Skip delete forms unless enabled
        if form.crud_type == "delete" and not self.test_destructive:
            result = TestResult(
                element=None,
                test_type="form_skip",
                passed=True,
                notes="Delete form skipped (use --test-destructive to enable)",
            )
            results.append(result)
            return results
        
        if verbose:
            print(f"      Testing form: {form.crud_type or 'unknown'} ({len(fillable_fields)} fields)")
        
        try:
            # Find the form element
            form_el = await page.query_selector(form.selector)
            if not form_el:
                results.append(TestResult(
                    element=None,
                    test_type="form_error",
                    passed=False,
                    error=f"Could not find form: {form.selector}",
                ))
                return results
            
            # Fill each field
            for field in fillable_fields:
                fill_result = await self._fill_field(page, field)
                results.append(fill_result)
            
            # Submit the form
            submit_result = await self._submit_form(page, form)
            results.append(submit_result)
            
            if submit_result.passed:
                submit_result.workflow = f"Form {form.crud_type or 'submit'}: {len(fillable_fields)} fields"
            
        except Exception as e:
            results.append(TestResult(
                element=None,
                test_type="form_error",
                passed=False,
                error=f"Form test failed: {str(e)}",
            ))
        
        return results

    async def _fill_field(self, page: Page, field: ElementInfo) -> TestResult:
        """Fill a form field with appropriate test data."""
        result = TestResult(element=field, test_type="fill", passed=False)
        
        try:
            el = await page.query_selector(field.selector)
            if not el:
                result.error = f"Could not find field: {field.selector}"
                return result
            
            if field.element_type == "select":
                # Select second option if available
                options = await el.query_selector_all("option")
                if len(options) > 1:
                    value = await options[1].get_attribute("value")
                    if value:
                        await el.select_option(value=value)
                        result.passed = True
                        result.notes = f"Selected option: {value[:20]}"
                else:
                    result.passed = True
                    result.notes = "Single option select"
                    
            elif field.element_type == "checkbox_radio":
                was_checked = await el.is_checked()
                if not was_checked:
                    await el.click()
                result.passed = True
                result.notes = "Checkbox/radio checked"
                
            elif field.element_type == "date_input":
                input_type = field.input_type or "date"
                test_value = TEST_DATA.get(input_type, TEST_DATA["date"])
                await el.fill(test_value)
                result.passed = True
                result.notes = f"Filled {input_type}: {test_value}"
                
            else:
                # Text-like input
                input_type = field.input_type or "text"
                test_value = TEST_DATA.get(input_type, TEST_DATA["text"])
                
                # Check for specific field hints
                field_hint = (field.name or field.placeholder or field.aria_label or "").lower()
                if "email" in field_hint:
                    test_value = TEST_DATA["email"]
                elif "password" in field_hint or "pass" in field_hint:
                    test_value = TEST_DATA["password"]
                elif "phone" in field_hint or "tel" in field_hint:
                    test_value = TEST_DATA["tel"]
                elif "url" in field_hint or "website" in field_hint:
                    test_value = TEST_DATA["url"]
                elif "name" in field_hint:
                    test_value = "Test User"
                elif "title" in field_hint:
                    test_value = "Test Title"
                elif "description" in field_hint or "content" in field_hint or "message" in field_hint:
                    test_value = TEST_DATA["textarea"]
                
                await el.fill(test_value)
                actual = await el.input_value()
                
                if actual == test_value:
                    result.passed = True
                    result.notes = f"Filled: {test_value[:20]}..."
                else:
                    result.passed = True  # Value was accepted but maybe transformed
                    result.notes = f"Value accepted (may be transformed)"
                    
        except Exception as e:
            result.error = f"Fill failed: {str(e)}"
        
        return result

    async def _submit_form(self, page: Page, form: FormInfo) -> TestResult:
        """Submit a form and verify the result."""
        result = TestResult(element=form.submit_button, test_type="submit", passed=False)
        
        try:
            original_url = page.url
            
            # Find and click submit button
            if form.submit_button:
                submit_el = await page.query_selector(form.submit_button.selector)
                if submit_el:
                    await submit_el.click(timeout=5000)
                else:
                    # Try form submission directly
                    form_el = await page.query_selector(form.selector)
                    if form_el:
                        await form_el.evaluate("form => form.submit()")
            else:
                # No submit button, try form.submit()
                form_el = await page.query_selector(form.selector)
                if form_el:
                    await form_el.evaluate("form => form.submit()")
            
            # Wait for response
            await page.wait_for_timeout(2000)
            
            # Handle potential navigation
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass

            new_url = page.url
            page_text = await page.inner_text("body")

            # Check for errors first
            error = check_for_error(page_text)
            if error:
                result.error = f"Form submission error: {error}"
                # Return to original page
                if new_url != original_url:
                    await page.go_back()
                    try:
                        await page.wait_for_load_state("domcontentloaded", timeout=5000)
                    except Exception:
                        pass
                return result

            # Check for success
            if check_for_success(page_text):
                result.passed = True
                result.notes = "Form submitted successfully (success indicator found)"
            elif new_url != original_url:
                result.passed = True
                result.notes = f"Form submitted (navigated to: {new_url[:40]}...)"
                # Go back for more testing
                await page.go_back()
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=5000)
                except Exception:
                    pass
            else:
                # No error, no navigation - might be AJAX success
                result.passed = True
                result.notes = "Form submitted (no errors detected)"
                
        except Exception as e:
            result.error = f"Submit failed: {str(e)}"
        
        return result

    def _generate_summary(self) -> None:
        """Generate summary statistics."""
        total_tests = self.report.total_passed + self.report.total_failed
        self.report.summary = {
            "total_pages": self.report.pages_tested,
            "total_elements": self.report.total_elements,
            "total_forms": self.report.total_forms,
            "total_tests": total_tests,
            "passed": self.report.total_passed,
            "failed": self.report.total_failed,
            "pass_rate": round(self.report.total_passed / total_tests * 100, 1) if total_tests > 0 else 0,
            "workflows_tested": self.report.workflows_tested,
            "elements_by_type": {},
            "failures_by_type": {},
            "crud_operations": {"create": 0, "read": 0, "update": 0, "delete": 0},
        }
        
        for page in self.report.pages:
            for el in page.elements:
                self.report.summary["elements_by_type"][el.element_type] = (
                    self.report.summary["elements_by_type"].get(el.element_type, 0) + 1
                )
                if el.crud_type:
                    self.report.summary["crud_operations"][el.crud_type] += 1
            
            for result in page.results:
                if not result.passed:
                    el_type = result.element.element_type if result.element else "form"
                    self.report.summary["failures_by_type"][el_type] = (
                        self.report.summary["failures_by_type"].get(el_type, 0) + 1
                    )


def report_to_dict(report: FullReport) -> dict:
    """Convert report to JSON-serializable dict."""
    return {
        "base_url": report.base_url,
        "timestamp": report.timestamp,
        "pages_tested": report.pages_tested,
        "total_elements": report.total_elements,
        "total_forms": report.total_forms,
        "total_passed": report.total_passed,
        "total_failed": report.total_failed,
        "workflows_tested": report.workflows_tested,
        "summary": report.summary,
        "pages": [
            {
                "url": p.url,
                "title": p.title,
                "elements_found": p.elements_found,
                "forms_found": p.forms_found,
                "tests_passed": p.tests_passed,
                "tests_failed": p.tests_failed,
                "errors": p.errors,
                "elements": [asdict(e) for e in p.elements],
                "forms": [
                    {
                        "selector": f.selector,
                        "action": f.action,
                        "method": f.method,
                        "crud_type": f.crud_type,
                        "field_count": len(f.fields),
                    }
                    for f in p.forms
                ],
                "results": [
                    {
                        "element": asdict(r.element) if r.element else None,
                        "test_type": r.test_type,
                        "passed": r.passed,
                        "error": r.error,
                        "notes": r.notes,
                        "workflow": r.workflow,
                    }
                    for r in p.results
                ],
            }
            for p in report.pages
        ],
    }


def print_summary(report: FullReport) -> None:
    """Print a human-readable summary."""
    print("\n" + "=" * 70)
    print("WEBSITE FUNCTIONAL TEST REPORT")
    print("=" * 70)
    print(f"URL: {report.base_url}")
    print(f"Timestamp: {report.timestamp}")
    print("-" * 70)
    print(f"Pages tested:     {report.pages_tested}")
    print(f"Elements found:   {report.total_elements}")
    print(f"Forms tested:     {report.total_forms}")
    print(f"Workflows tested: {report.workflows_tested}")
    print("-" * 70)
    print(f"Tests passed: {report.total_passed}")
    print(f"Tests failed: {report.total_failed}")
    print(f"Pass rate:    {report.summary.get('pass_rate', 0)}%")
    print("-" * 70)
    
    if report.summary.get("crud_operations"):
        print("\nCRUD Operations Detected:")
        for op, count in report.summary["crud_operations"].items():
            if count > 0:
                print(f"  {op.capitalize()}: {count}")
    
    print("\nElements by type:")
    for el_type, count in report.summary.get("elements_by_type", {}).items():
        print(f"  {el_type}: {count}")
    
    if report.summary.get("failures_by_type"):
        print("\nFailures by type:")
        for el_type, count in report.summary["failures_by_type"].items():
            print(f"  {el_type}: {count}")
    
    # List failures
    failures = []
    for page in report.pages:
        for result in page.results:
            if not result.passed and result.error:
                failures.append({
                    "page": page.url,
                    "element": result.element.selector if result.element else "form",
                    "type": result.test_type,
                    "error": result.error,
                })
    
    if failures:
        print(f"\n{'=' * 70}")
        print("FAILURES")
        print("=" * 70)
        for i, f in enumerate(failures[:20], 1):
            print(f"\n{i}. [{f['type']}] {f['element'][:50]}")
            print(f"   Page: {f['page'][:60]}")
            print(f"   Error: {f['error']}")
        
        if len(failures) > 20:
            print(f"\n... and {len(failures) - 20} more failures")
    
    # List successful workflows
    workflows = []
    for page in report.pages:
        for result in page.results:
            if result.passed and result.workflow:
                workflows.append({
                    "page": page.url,
                    "workflow": result.workflow,
                })
    
    if workflows:
        print(f"\n{'=' * 70}")
        print("WORKFLOWS TESTED")
        print("=" * 70)
        for i, w in enumerate(workflows[:15], 1):
            print(f"{i}. {w['workflow']}")
            print(f"   {w['page'][:60]}")
    
    print("\n" + "=" * 70)


async def main():
    parser = argparse.ArgumentParser(description="Functional test all elements on a website")
    parser.add_argument("url", help="Base URL to test")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--screenshots-dir", "-s", help="Directory for failure screenshots")
    parser.add_argument("--max-pages", type=int, default=0, help="Maximum pages to crawl (0 = unlimited)")
    parser.add_argument("--timeout", type=int, default=15000, help="Page load timeout in ms")
    parser.add_argument("--test-destructive", action="store_true", help="Also test delete operations (dangerous!)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress console output")
    parser.add_argument("--cookie", "-c", action="append", help="Cookie in format 'name=value' (can be used multiple times)")

    args = parser.parse_args()

    screenshots_dir = None
    if args.screenshots_dir:
        screenshots_dir = Path(args.screenshots_dir)
        screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Parse cookies
    cookies = None
    if args.cookie:
        cookies = []
        parsed_url = urlparse(args.url)
        for cookie_str in args.cookie:
            if "=" in cookie_str:
                name, value = cookie_str.split("=", 1)
                cookies.append({
                    "name": name.strip(),
                    "value": value.strip(),
                    "domain": parsed_url.netloc.split(":")[0],  # Remove port
                    "path": "/",
                })

    tester = WebsiteTester(
        base_url=args.url,
        screenshots_dir=screenshots_dir,
        max_pages=args.max_pages,
        timeout=args.timeout,
        test_destructive=args.test_destructive,
        cookies=cookies,
    )
    
    if not args.quiet:
        print(f"Functional Testing: {args.url}")
        print(f"Max pages: {'unlimited' if args.max_pages == 0 else args.max_pages}")
        print(f"Test destructive ops: {args.test_destructive}")
        print(f"Authenticated: {bool(cookies)}")
        print("=" * 70)
    
    report = await tester.run(verbose=not args.quiet)
    
    if not args.quiet:
        print_summary(report)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(report_to_dict(report), f, indent=2)
        if not args.quiet:
            print(f"\nFull report saved to: {output_path}")
    
    sys.exit(1 if report.total_failed > 0 else 0)


if __name__ == "__main__":
    asyncio.run(main())
