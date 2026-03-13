# CourierFlow Data Models Reference

## User (`users` table, `app/models/user.py`)
- PK: `id` (GUID/UUID)
- Auth: `email` (unique, indexed), `password_hash`
- Profile: `full_name`, `phone`, `timezone` (default "UTC"), `email_send_time` (default 9:00 AM)
- Gmail OAuth: `gmail_refresh_token`, `gmail_token_expires_at`, `gmail_auth_status` (GmailAuthStatus enum)
- Google Calendar: `google_calendar_token`, `google_calendar_refresh_token`
- Outlook: separate tokens for calendar and email
- 2FA: `twofa_enabled`, `twofa_secret`, `twofa_backup_codes`
- AI: `ai_daily_digest_enabled`, `ai_proactive_suggestions_enabled`
- Billing: `stripe_customer_id`, `stripe_subscription_id`, `subscription_plan` (free/pro), `subscription_status`
- Onboarding: `onboarding_profile`, `onboarding_step`, `onboarding_completed`
- Cached counts: `property_count`, `sequence_count`
- Industry: `business_name`, `industry_preset`, `terminology_config` (JSON), `client_types_config` (JSON)
- Key relationships: clients, properties, contacts, workflow_templates, calendar_events, documents, emails

## Property (`properties` table, `app/models/property.py`)
- PK: `id` (GUID), FK: `user_id`
- Name: `name` (optional display name)
- Classification: `client_type` (HouseholdType enum - legacy), `account_type` (String - new), `status` (HouseholdStatus: active/hold/archived)
- RE legacy: `property_address`, `budget_min/max`, `bedrooms`, `bathrooms`, `property_type`
- Landlord: `unit_count`, `year_built`, `square_footage`, `parking_info`, `trash_day`, `hoa_name/fee/contact`, `utility_providers` (JSON), `lease_terms_default` (JSON)
- Location: `city`, `state` (2-char code)
- Custom: `custom_data` (JSON), `tags` (JSONEncodedArray)
- Key relationships: user, members (HouseholdMember, eager selectin), units (PropertyUnit, eager selectin), workflow_instances, calendar_events
- Helper props: `display_name`, `display_type`, `primary_contact`, `all_emails`, `all_phones`
- Max 10 members per property (enforced via event listener)

## HouseholdMember (`household_members` table, `app/models/property.py`)
- PK: `id` (GUID), FK: `household_id` -> properties (with `property_id` synonym)
- Identity: `first_name`, `last_name`, `email`, `phone`
- Role: `role` (String), `is_primary_contact` (Boolean)
- Comm prefs: `receive_emails`, `receive_sms`, `do_not_message` (master opt-out)
- Lease: `unit_id` (FK -> property_units), `lease_start`, `lease_end`, `rent_amount` (cents), `move_in_date`, `move_out_date`
- Contact prefs: `preferred_contact_channel`, `no_contact_start_hour`, `no_contact_end_hour`, `no_contact_days` (JSON)
- `user_id` FK for user-scoped queries
- One primary contact enforced via `ensure_one_primary` event listener

## PropertyUnit (`property_units` table, `app/models/property.py`)
- PK: `id` (GUID), FK: `household_id` -> properties
- `unit_label` (e.g., "2B", "Basement"), unique per property
- Physical: `bedrooms`, `bathrooms`, `square_footage`
- Financial: `rent_amount` (cents)
- Status: `is_occupied`

## Client (`clients` table, `app/models/client.py`)
- Uses `Mapped[]` style (SQLAlchemy 2.0 mapped_column)
- PK: `id` (GUID), FK: `user_id`, `household_id` (-> properties)
- Identity: `first_name`, `last_name`, `email`, `phone`
- Normalized: `email_normalized`, `phone_normalized`
- Classification: `client_type` (ClientType enum - legacy), `contact_type` (String - new), `status` (ClientStatus: lead/qualified/active/under_contract/closed/inactive)
- Status transitions enforced via `ClientStatus.can_transition()`
- `tags` with GIN index, `custom_data` JSON
- Many indexes including trigram for fuzzy search

## WorkflowTemplate (`workflow_templates` table, `app/models/workflow.py`)
- PK: `id` (GUID), FK: `user_id`
- `name`, `description`, `trigger` (WorkflowTrigger enum), `client_types` (JSON)
- State: `state` (draft/published/archived), `folder_id`, `parent_id` (for clones)
- Auto-pause: `auto_pause_enabled`, `auto_pause_threshold` (default 3)
- Relationships: steps (ordered by step_order), instances, versions, folder, permissions

## WorkflowTemplateStep (`workflow_template_steps` table, `app/models/workflow.py`)
- PK: `id` (GUID), FK: `template_id`
- `step_order`, `name`, `description`
- Action: `action_type` (WorkflowActionType enum - UPPERCASE), `action_config` (JSON)
- Timing: `delay_days`, `delay_hours`, `timing_type` (StepTimingType), `relative_days`, `specific_date`
- Branching: `conditions` (JSON), `branch_true_step_id`, `branch_false_step_id`
- Recurring: `is_recurring`, `recurrence_interval`, `max_recurrences`
- Error: `max_retries`, `retry_delay_minutes`, `continue_on_error`
- Recipient: `recipient_type` (TENANT/LANDLORD/BOTH)
- UI: `ui_position_x`, `ui_position_y` (for visual builder)

## WorkflowInstance (`workflow_instances` table, `app/models/workflow.py`)
- PK: `id` (GUID), FKs: `template_id`, `client_id` (deprecated), `household_id`, `user_id`, `calendar_event_id`
- Status: `status` (WorkflowInstanceStatus), `current_step_order`
- Tracking: `started_at`, `completed_at`, `next_action_at`
- Target date: `target_date`, `target_date_label`
- Pause: `paused_at`, `paused_by_user_id`, `resume_date`, `pause_reason`
- Email engagement: `consecutive_unopened_emails`, `auto_paused`
- Delivery: `consecutive_delivery_failures`
- Error: `error_count`, `last_error`
- CHECK constraint: `NOT (client_id IS NULL AND household_id IS NULL)`
- Many partial indexes for scheduler queries

## WorkflowInstanceStep (`workflow_instance_steps` table, `app/models/workflow.py`)
- PK: `id` (GUID), FKs: `instance_id`, `template_step_id`
- `step_order`, `status` (WorkflowStepStatus)
- Timing: `scheduled_at`, `started_at`, `completed_at`
- Results: `result_data` (JSON), `error_message`, `retry_count`
- Email: `email_sent`, `email_sent_at`, `email_opened`, `email_opened_at`
- Draft: `saved_as_draft`, `draft_content` (JSON), `cancelled_at`
- Recipient: `recipient_override`
- Idempotency: `send_idempotency_key` (unique)

## CalendarEvent (`calendar_events` table, `app/models/calendar.py`)
- PK: `id` (GUID), FK: `user_id`, `client_id`, `household_id`, `workflow_instance_id`, `task_id`
- Details: `title`, `description`, `location`
- Timing: `start_time`, `end_time`, `all_day_event`, `timezone`
- Type: `event_type` (CalendarEventType enum)
- External: `provider`, `external_event_id`, `external_calendar_id`
- Sync: `sync_status`, `sync_hash`, `sync_version`, `needs_sync`
- Recurring: `is_recurring`, `recurrence_rule`, `parent_event_id`
- Indexes: unique on (provider, external_event_id), composite on (user_id, start_time)

## CalendarEventMeta (`calendar_event_meta` table, `app/models/event_type.py`)
- 1:1 with CalendarEvent via `calendar_event_id` (unique)
- Detection: `detected_event_type`, `parsing_method`, `confidence`
- Matched: `matched_household_id`, `matched_unit_id`, `matched_member_id`
- Manual overrides (sticky): `manual_event_type`, `manual_household_id`, etc.
- Status: `confirmation_status` (pending/confirmed/rejected)
- Ambiguity: `is_ambiguous`, `ambiguity_reason`

## EventTypeMapping (`event_type_mappings` table, `app/models/event_type.py`)
- Links event_type -> WorkflowTemplate with scope (global/property/unit)
- Priority: unit(20) > property(10) > global(0)
- `default_recipient_type`, `is_active`

## EventTypeAlias (`event_type_aliases` table, `app/models/event_type.py`)
- User-defined keyword aliases for event types
- `alias` -> `event_type` mapping, unique per user

## Other Key Models
- `WorkflowApproval`: Approval gates for steps (pending/approved/rejected/timeout)
- `WorkflowAuditLog`: Complete audit trail
- `EmailEngagementTracking`: Bridge for email open tracking + auto-pause
- `SendWindow`: Per-user send time rules
- `AIEmailSuggestion`: AI-generated email suggestions
- `EventSyncLog`, `CalendarSyncState`, `CalendarWebhook`, `CalendarIntegration`: Calendar sync infrastructure
- `SyncConflict`: Persisted calendar sync conflicts
- Workflow Builder: `WorkflowTemplateVersion`, `WorkflowFolder`, `WorkflowDependency`, `WorkflowTemplatePermission`, `StepNote`
