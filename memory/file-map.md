# CourierFlow File Map

## App Structure
```
app/
├── config.py              # Settings(BaseSettings) - env vars
├── exceptions.py          # AppException hierarchy + HTTP factories
├── main.py                # FastAPI app, middleware, router includes
├── database/
│   ├── __init__.py        # GUID, Base, JSONEncodedArray, get_db, init_db, engine
│   └── encrypted.py       # EncryptedColumn, encryption utilities
├── models/                # SQLAlchemy models (see models.md)
├── schemas/               # Pydantic schemas (request/response)
├── routes/                # FastAPI routers (thin)
├── services/              # Business logic (thick)
├── templates/             # Jinja2 HTML
│   ├── base.html          # Main layout with blocks
│   ├── macros/ui_macros.html  # Reusable UI macros
│   └── ...
├── static/
│   ├── css/design-system/_variables.css  # --ds-* CSS variables
│   └── js/workflow-builder/              # Vue 3 workflow builder
└── utils/
    └── prompt_sanitizer.py  # Mandatory for AI calls
```

## Key Config (app/config.py)
- `database_url`: default sqlite+aiosqlite for testing
- `secret_key`, `debug`, `environment`
- OAuth: `google_client_id/secret`, `microsoft_client_id/secret`
- AI: `openai_api_key`, `anthropic_api_key`, `ai_provider` (auto/anthropic/openai)
- Billing: Stripe keys
- DocuSign, Twilio, Zoom configs

## Routes (app/routes/) - All thin, delegate to services
- `auth.py` - Login, signup, Google OAuth
- `dashboard.py` - Main dashboard
- `calendar.py` - Google Calendar integration
- `workflows.py` - Workflow/sequence CRUD
- `workflow_builder.py` - Drag-and-drop builder UI
- `workflow_ai.py` - AI content generation
- `households.py` - Property + tenant management
- `documents.py` / `document_upload.py` - Document storage
- `email.py` / `email_templates.py` - Email sending + templates
- `sms.py` - Twilio SMS
- `event_meta.py` - Calendar event meta: confirm, reject, override, reparse
- `event_types.py` - Event type listing + mapping CRUD
- `addon.py` - Google Calendar Sidebar endpoints
- `billing.py` - Stripe billing
- `webhooks.py` - Google Calendar webhooks
- `analytics.py` - Insights
- `automations.py` - Automation engine
- `tenant_actions.py` - Tenant magic-link action pages

## Services (app/services/) - Business logic
**Workflow**: workflow_service, workflow_executor, workflow_scheduler, workflow_validation_service, workflow_ai_service
**Calendar**: calendar_service, calendar_sync_service
**Event**: event_detection_service, event_type_service, event_meta_service
**Communication**: email, email_template_service, sms, multi_channel_service, communication_history_service
**Data**: household_service, document_checklist_service, tenant_action_service
**Documents**: document_delivery_service, docusign_service
**Auth**: auth, google_oauth, magic_link_service
**AI**: openai_service, ai_rate_limiter, ai_cost_tracker
**Billing**: stripe_service, stripe_webhook_handler, billing_service
**Templates**: landlord_templates_service, template_version_service, template_clone_service
**Analytics**: execution_insights_service, proactive_alert_service, workflow_suggestion_service
**Infrastructure**: pending_operations_service, dashboard_cache_service, send_window_service

## Schema Files (app/schemas/)
- `workflow.py` - WorkflowCreate, WorkflowUpdate, WorkflowResponse, etc.
- `property.py` - PropertyCreate, PropertyUpdate, MemberCreate, etc.
- `client.py` - ClientCreate, ClientUpdate, ClientResponse
- `event_type.py` - EventTypeMapping schemas
- `user.py` - UserCreate, UserUpdate, UserResponse
- `addon.py` - Google Calendar Sidebar schemas
- `workflow_builder.py` - Builder-specific schemas
- `analytics_schemas.py` - Dashboard analytics

## Tests (tests/)
- Uses pytest with async support
- `conftest.py` has fixtures for test DB, test user, test client
- SQLite for tests (in-memory)
