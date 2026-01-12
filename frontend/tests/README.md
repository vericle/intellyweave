# Frontend E2E Tests

Playwright-based end-to-end tests for the IntellyWeave frontend.

## Configuration

The Playwright configuration is optimized for IntellyWeave as a **desktop application**:

- **Viewport**: 1920x1080 (Full HD Desktop) - set globally in `playwright.config.ts`
- **Persistent Context**: Storage state is saved and reused across test sessions
- **Startup Dialog**: Automatically bypassed using pre-configured local storage settings

## Directory Structure

```bash
tests/
├── setup/
│   └── auth.setup.ts                         # Setup script to configure local storage
├── state/
│   └── storage-state.json                    # Persistent browser state (auto-generated, gitignored)
├── fixtures/
│   └── recording.ts                          # Custom recording fixture for interactive tests
├── output/                                   # Test outputs (excluded from test discovery)
│   ├── recordings/                           # Interactive recording sessions
│   │   └── recording-{name}-{timestamp}/
│   │       ├── screenshots/                  # Interaction screenshots
│   │       ├── network/                      # Network request/response JSON files
│   │       ├── console/                      # Console logs
│   │       ├── recorded-actions.json         # Complete action timeline
│   │       ├── network-requests.json         # All network requests
│   │       ├── console-logs.json             # All console logs
│   │       └── generated-test.ts.template    # Template for automated test
│   ├── test-results/                         # Test artifacts (screenshots, videos, traces)
│   └── playwright-report/                    # HTML test reports
├── network-chart.interactive.spec.ts         # Interactive network chart recording test
└── README.md
```

## Local Storage Configuration

The following local storage settings are automatically configured to bypass startup dialogs:

- `INTELLYWEAVE_START_DIALOG_DONT_SHOW_AGAIN`: Prevents the startup configuration dialog
- `TLDRAW_USER_DATA_v3`: User preferences for TLDraw components
- `mapbox.eventData:*`: Mapbox telemetry settings
- `device_id`: Persistent device identifier
- `jam_ephemeral_events_content-interactivity-events`: Event tracking configuration

These settings are defined in:
1. `tests/state/storage-state.json` (version-controlled template)
2. `tests/setup/auth.setup.ts` (setup script that applies them)

## Setup

Playwright is already configured in `frontend/playwright.config.ts`.

### Install Browsers (First Time)

```bash
npx playwright install
```

### Initial Storage State Setup

The storage state is automatically configured on first test run. To manually regenerate:

```bash
pnpm exec playwright test --project=setup
```

## Running Tests

### Standard Tests

```bash
pnpm test
```

### Interactive Recording Mode (Manual Testing)

**Network Chart Recording:**

```bash
pnpm test:record:network
```

**All Interactive Tests:**

```bash
pnpm test:record
```

This runs interactive recording sessions with:
- **Headed mode** (browser visible)
- **Full network recording** (requests, responses, timing)
- **Console log capture** (all levels)
- **Click tracking with screenshots** (automatic selector generation)
- **React render detection** (MutationObserver-based)
- **1-hour timeout** (prevents runaway tests)
- **Auto-generates test template** from your interactions

**Important**: The generated test files are saved as `.ts.template` files, not `.spec.ts`, to prevent them from running automatically. To use a generated test:
1. Rename `generated-test.ts.template` to `your-test.spec.ts`
2. Add assertions and validation logic
3. Move to appropriate test directory

## Test Structure

### Interactive Recording Tests (`.interactive.spec.ts`)

Interactive manual testing sessions with comprehensive recording capabilities.

**Available Tests:**
- `network-chart.interactive.spec.ts` - Network chart visualization testing

**Features:**
- ✅ Network request/response capture (JSON bodies for API calls)
- ✅ Console log monitoring (all levels)
- ✅ Click tracking with auto-generated CSS selectors
- ✅ React component render detection via MutationObserver
- ✅ Screenshot on every interaction
- ✅ 1-hour timeout (prevents runaway tests)
- ✅ Auto-generates test template from recorded session

**Custom Recording Fixture:**

The interactive tests use a custom Playwright fixture (`tests/fixtures/recording.ts`) that provides more comprehensive tracking than Playwright's built-in recording:
- Click detection with selector generation
- React render monitoring
- Network request/response capture
- Console log aggregation
- Automatic test code generation

**Output Location:**
- `tests/output/recordings/recording-{name}-{timestamp}/`
  - `screenshots/` - Every interaction captured with sequential numbering
  - `network/` - All network requests as individual JSON files
  - `console/` - Console log entries
  - `recorded-actions.json` - Complete action timeline with timestamps
  - `network-requests.json` - Aggregated network data
  - `console-logs.json` - Aggregated console logs
  - `generated-test.ts.template` - Test template (requires manual editing)

## Writing New Tests

1. Create a new `.spec.ts` file in the `tests/` directory
2. Import Playwright test utilities:

```typescript
import { test, expect } from '@playwright/test';
```

3. Write your tests following the existing patterns

## Continuous Integration

Tests automatically run in CI when:
- Creating pull requests
- Pushing to main branch

## Storage State Management

### How It Works

1. **Initial Setup**: The `auth.setup.ts` script runs before all tests
2. **Local Storage**: Settings are injected into the browser's local storage
3. **State Saving**: The browser state is saved to `tests/state/storage-state.json`
4. **State Reuse**: All subsequent tests load this saved state automatically

### Regenerating Storage State

If you need to update the local storage settings:

1. Edit `tests/setup/auth.setup.ts` with new values
2. Delete `tests/state/storage-state.json` (if it exists)
3. Run the setup:

   ```bash
   pnpm exec playwright test --project=setup
   ```

The storage state will be regenerated and saved for future test runs.

## Test Projects

The Playwright configuration includes multiple browser projects:

- **setup**: Runs first to configure application settings
- **chromium**: Chrome/Edge browser tests (depends on setup)
- **firefox**: Firefox browser tests (depends on setup)
- **webkit**: Safari browser tests (depends on setup)
- **interactive-recording**: Interactive manual testing with custom recording fixture

All browser projects depend on the setup project, ensuring local storage is configured before tests run.

### Interactive Recording Project

The `interactive-recording` project has special configuration:
- Matches only `*.interactive.spec.ts` files
- Runs in headed mode (browser visible)
- Uses custom recording fixture instead of built-in Playwright recording
- Trace, screenshot, and video are disabled (custom fixture provides better tracking)
- 100ms slowMo for easier observation

## Desktop Application Focus

IntellyWeave is primarily a desktop application. The test configuration reflects this:

- Default viewport: **1920x1080** (Full HD Desktop)
- No mobile viewport tests enabled by default
- Focus on desktop interactions and layouts

To test mobile viewports, uncomment the mobile projects in `playwright.config.ts`.

## Debugging Failed Tests

When tests fail, Playwright generates:
- **Screenshots** (in `test-results/`)
- **Videos** (in `test-results/`)
- **Traces** (viewable with `npx playwright show-trace trace.zip`)

### Troubleshooting

#### Tests show startup dialog

- Delete `tests/state/storage-state.json`
- Run setup project: `pnpm exec playwright test --project=setup`

#### Viewport size incorrect

- Check `playwright.config.ts` viewport configuration
- Remove any manual `page.setViewportSize()` calls in tests

#### Storage state not persisting

- Verify `storageState` path in `playwright.config.ts`
- Ensure setup project runs before browser projects
- Check that `tests/state/` directory exists

## Interactive Recording Workflow

### Starting a Recording Session

1. **Start the recording**:

   ```bash
   cd frontend
   pnpm test:record
   ```

2. **The script will**:
   - Start both backend and frontend servers (via `scripts/dev.sh`)
   - Open Chrome browser in headed mode
   - Navigate to the application
   - Begin monitoring all interactions

3. **Manually test your application**:
   - Click elements, navigate pages, interact with components
   - Every action is automatically captured
   - Console output shows real-time tracking

4. **End the session**:
   - Close the browser window, or
   - Press `Ctrl+C` in the terminal

5. **Review the recording**:
   - Check `tests/output/recordings/recording-{name}-{timestamp}/`
   - Review screenshots, network calls, console logs
   - Use `generated-test.ts.template` as starting point for automated tests

### Generated Test Templates

The session automatically creates a test template file (`generated-test.ts.template`) with:
- All clicks converted to `page.locator().click()` commands
- Proper wait conditions
- CSS selectors for each element
- Comments showing what was clicked

**Important**: These are templates, not ready-to-run tests. To use them:

1. **Rename the file**:

   ```bash
   mv generated-test.ts.template my-new-test.spec.ts
   ```

2. **Add assertions**:

   ```typescript
   // Before (generated template)
   await page.locator('button.submit').click();
   await page.waitForLoadState('networkidle');
   // Add your assertions here

   // After (with assertions)
   await page.locator('button.submit').click();
   await page.waitForLoadState('networkidle');
   await expect(page.locator('.success-message')).toBeVisible();
   ```

3. **Move to test directory** (if outside `tests/output/`):

   ```bash
   mv my-new-test.spec.ts tests/
   ```

### Why `.ts.template` instead of `.spec.ts`?

Generated test files use the `.ts.template` extension to prevent Playwright from automatically discovering and running them. This prevents:
- Incomplete tests from running in CI
- Infinite loops (new recordings generating more tests)
- Test failures from missing assertions

The `testIgnore: '**/output/**'` configuration in `playwright.config.ts` also ensures that all files in the output directory are excluded from test discovery.

## Resources

- [Playwright Documentation](https://playwright.dev)
- [IntellyWeave Design System](../docs/design-system.md)
- [Test Configuration](../playwright.config.ts)
