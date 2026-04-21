## Playwright MCP Tools Reference

### Navigation
- `browser_navigate`: Go to URL
- `browser_navigate_back`: Go back in history

### Inspection
- `browser_snapshot`: Get accessibility tree with element refs (PREFERRED)
- `browser_take_screenshot`: Capture visual screenshot

### Interaction
- `browser_click`: Click element by ref
- `browser_type`: Type text into element
- `browser_fill_form`: Fill multiple form fields
- `browser_select_option`: Select dropdown option
- `browser_hover`: Hover over element
- `browser_press_key`: Press keyboard key

### Waiting
- `browser_wait_for`: Wait for text, text gone, or time

### Utilities
- `browser_resize`: Change viewport size
- `browser_console_messages`: Get console logs
- `browser_network_requests`: Get network activity
- `browser_tabs`: Manage browser tabs
- `browser_evaluate`: Run JavaScript
- `browser_close`: Close browser

## Best Practices

1. **Always take snapshots** before and after interactions
2. **Use refs from snapshots** for accurate element targeting
3. **Wait appropriately** for dynamic content to load
4. **Handle modals** that may block interactions
5. **Test both happy path and edge cases**
6. **Document all findings** with evidence

## Quick Start Commands

### Run Full Test Suite
```
1. Ask for credentials
2. Login to production site
3. Execute all critical path tests
4. Generate summary report
```

### Run Single Feature Tests
```
1. Ask which feature area
2. Run only those user stories
3. Report results
```

### Smoke Test
```
1. Login
2. Navigate to each main section
3. Verify pages load without errors
4. Report any issues
```

## Troubleshooting

### Common Issues

1. **Element not found**: Take fresh snapshot, check element visibility
2. **Login fails**: Verify credentials, check for 2FA requirement
3. **Modal blocking**: Use browser_click to dismiss, or browser_evaluate to close
4. **Timeout**: Increase wait time, check network status
5. **Wrong page**: Use browser_snapshot to verify current URL/content

### Debug Mode

For detailed debugging:
1. Take screenshot at each step
2. Check browser_console_messages for errors
3. Check browser_network_requests for failed API calls
4. Use browser_evaluate to inspect page state

