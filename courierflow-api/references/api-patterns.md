# CourierFlow API Patterns

## Route Shape

Use this route flow:

1. dependency injection and auth
2. Pydantic/request validation
3. call one service method
4. convert domain exceptions to HTTP errors
5. return response schema or redirect

Do not put calendar parsing, workflow arming, scheduler calculations, or
message routing in route functions.

## Service Shape

Services should:

- accept `AsyncSession` and current user/user id explicitly
- scope reads and writes by `user_id`
- raise domain exceptions, not `HTTPException`
- leave transaction ownership to the route or caller
- isolate auxiliary side effects like email, SMS, logs, and notifications
- use structured logs with enough context to diagnose one landlord's issue

## Exception Mapping

Routes map service exceptions as:

| Domain exception | HTTP |
| --- | --- |
| `NotFoundError` | 404 |
| `ValidationError` | 422 |
| `AuthorizationError` | 403 |
| `ExternalServiceError` | 502 |
| `ConflictError` | 409 |

Never expose stack traces, provider payloads, SQL text, or token details.

## Workflow Confirmation Rules

- Calendar parser output is proposed state until the landlord confirms.
- Ambiguous matches stay pending.
- Workflow creation snapshots template state.
- Scheduled timestamps are calculated eagerly.
- Event date changes recalculate pending steps only.
- Event deletion pauses linked instances.
- Opt-out blocks workflow execution unless the landlord explicitly overrides a
  step.

## Query Checks

- Every route or service that reads user data filters by `user_id`.
- Use eager loading (`selectinload` / `joinedload`) for related property,
  tenant, event, workflow, and step data shown together.
- Use cursor pagination for new list endpoints.
- Avoid `scalar_one_or_none()` unless backed by a uniqueness constraint.

## Test Expectations

Cover:

- success path
- not found or wrong-user access
- validation/business-rule failure
- external-service failure when relevant
- pending/confirmed workflow status transition when relevant

## CopilotKit Action handler typing

- **`useCopilotAction` handler stubs that just `JSON.stringify` args should drop the explicit `args: <Input>` annotation.** When the v1.54+ `parameters: [...]` array doesn't fully line up with the Python-side `<Input>` interface (e.g. backend Action declares richer enum types like `step_type: StepType` while the frontend `parameters` declares `type: 'string'`), TS rejects the handler with `Parameters<typeof X>[0] is not assignable to <Input>`. For stub handlers whose body is `return JSON.stringify(args)`, drop the annotation — `args` flows from the parameters declaration and the body never reads typed fields. Don't extend this pattern to handlers that destructure or branch on args; those need accurate types and the right place to fix is the `parameters` declaration.
