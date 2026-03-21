# Active Codebase Reference

Files in active development. Everything else is in `_archived/` — do not import, modify, or reference archived files.

## Routes (`app/routes/`)

| File | Purpose |
|------|---------|
| `auth.py` | Login, signup, Google OAuth |
| `dashboard.py` | Main dashboard |
| `calendar.py` | Google Calendar integration |
| `workflows.py` | Workflow/sequence CRUD |
| `workflow_builder.py` | Drag-and-drop builder UI |
| `workflow_ai.py` | AI content generation for steps |
| `workflow_folders.py` | Workflow organization |
| `households.py` | Property + tenant management |
| `documents.py` | Document storage |
| `document_upload.py` | File upload handling |
| `uploads.py` | File uploads |
| `email.py` | Sending emails |
| `email_templates.py` | Email template CRUD |
| `sms.py` | Twilio SMS |
| `contact_import.py` | CSV tenant import |
| `automations.py` | Automation engine (calendar triggers) |
| `notifications.py` | Basic notifications |
| `health.py` | Health checks |
| `errors.py` | Error handlers |
| `preferences.py` | User preferences |
| `search.py` | Basic search |
| `webhooks.py` | Google Calendar webhooks |
| `ai_assistant.py` | Conversational AI for workflow building |
| `ai_suggestions.py` | AI-powered suggestions |
| `chat.py` | Chat UI for AI assistant |
| `chat_stream.py` | SSE streaming for AI chat |
| `event_types.py` | Event type listing + mapping CRUD |
| `event_meta.py` | Calendar event meta: confirm, reject, override, reparse |
| `customization.py` | Settings/customization |
| `nudges.py` | Adoption nudges API |
| `addon.py` | Google Calendar Sidebar endpoints |
| `docusign.py` | DocuSign envelope management |
| `tenant_actions.py` | Tenant magic-link action pages |
| `analytics.py` | Insights and analytics |
| `billing.py` | Stripe billing |
| `landing.py` | Landing pages |

## Services (`app/services/`)

**Workflow:** `workflow_service.py`, `workflow_executor.py`, `workflow_scheduler.py`, `workflow_validation_service.py`, `workflow_ai_service.py`

**Calendar:** `calendar_service.py`, `calendar_sync_service.py`

**Event detection:** `event_detection_service.py`, `event_type_service.py`, `event_meta_service.py`

**Communication:** `email.py`, `email_template_service.py`, `sms.py`, `inbound_response_service.py`, `multi_channel_service.py`, `communication_history_service.py`, `communication_qa_service.py`

**Data:** `household_service.py`, `document_checklist_service.py`, `client_field_service.py`, `condition_evaluator.py`, `tenant_action_service.py`

**Documents & Signing:** `document_delivery_service.py`, `docusign_service.py`

**Storage:** `storage_service.py`, `s3_service_optimized.py`

**Auth & infrastructure:** `auth.py`, `google_oauth.py`, `magic_link_service.py`, `url_shortener_service.py`, `notification_service.py`, `terminology_service.py`, `search_service_optimized.py`

**AI:** `openai_service.py`, `ai_rate_limiter.py`, `ai_cost_tracker.py`

**Billing:** `stripe_service.py`, `stripe_webhook_handler.py`, `billing_service.py`

**Onboarding:** `nudge_service.py`, `onboarding_service.py`

**Templates:** `landlord_templates_service.py`, `template_version_service.py`, `template_clone_service.py`, `template_variable_validator.py`, `template_analytics_service.py`, `template_quality_service.py`

**Analytics:** `execution_insights_service.py`, `proactive_alert_service.py`, `batch_workflow_service.py`, `workflow_suggestion_service.py`

**Infrastructure:** `data_health_service.py`, `maintenance_reminder_service.py`, `calendar_pattern_service.py`, `calendar_backup_service.py`, `dashboard_cache_service.py`, `impact_preview_service.py`, `send_window_service.py`, `pending_operations_service.py`

**Add-on:** `addon_card_builder.py`, `addon_calendar_service.py`

**AI assistant:** `ai/claude_chat_service.py`, `chat_service.py`

## Models (`app/models/`)

`user.py`, `household.py`, `workflow.py`, `workflow_builder.py`, `workflow_enums.py`, `calendar.py`, `event_type.py`, `document.py`, `document_checklist.py`, `email.py`, `email_template.py`, `communication_template.py`, `contact.py`, `client.py`, `task.py`, `notification.py`, `automation.py`, `file.py`, `integration.py`, `oauth_token.py`, `sms_log.py`, `action_log.py`, `inbound_response.py`, `tenant_action.py`

## Templates (`app/templates/`)

**Keep:** `base.html`, `base_modern.html`, `calendar.html`, `documents.html`, `email_templates.html`, `preferences.html`, `search.html`, `settings.html`, `uploads.html`, `insights.html`

**Keep directories:** `auth/`, `errors/`, `workflows/`, `households/`, `email/`, `templates/`, `partials/`, `macros/`, `landing/`, `onboarding/`, `tenant_action/`

## JavaScript (`app/static/js/`)

**Keep:** `workflow-builder/` (entire directory), `email-compose-modal.js`, `email_templates.js`, `dark-mode.js`, `drag-drop-upload.js`, `keyboard-shortcuts.js`, `modern-ui.js`, `notifications.js`, `search.js`, `ui-components.js`, `ui-components-advanced.js`

## File Governance Rule

If a change requires a file not listed here, add it to this file before editing.
