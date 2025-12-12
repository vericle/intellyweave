import { defineConfig, devices } from '@playwright/test';
import path from 'node:path';

/**
 * Playwright configuration for IntellyWeave frontend tests
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',

  /* Exclude output directories from test discovery to prevent generated tests from running */
  testIgnore: '**/output/**',

  /* Output directories - all under tests/ */
  outputDir: './tests/output/test-results',

  /* Run tests in files in parallel */
  fullyParallel: true,

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [['html', { outputFolder: './tests/output/playwright-report' }]],

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:3000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',

    /* Screenshot on failure */
    screenshot: 'only-on-failure',

    /* Video on failure */
    video: 'retain-on-failure',

    /* Desktop viewport size - primarily a desktop application */
    viewport: { width: 1920, height: 1080 },

    /* Persistent context for session reuse */
    storageState: path.join(__dirname, 'tests/state/storage-state.json'),

    /* Enable automatic waiting for navigation and network idle */
    actionTimeout: 30000,
    navigationTimeout: 60000,
  },

  /* Configure projects for major browsers */
  projects: [
    // Setup project to configure application settings
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },

    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },

    // Interactive manual testing with full recording
    // Note: Built-in Playwright recording (trace/screenshot/video) is disabled because
    // the custom recording fixture provides more comprehensive tracking:
    // - Click detection with selector generation
    // - React render monitoring
    // - Network request/response capture
    // - Console log aggregation
    // - Automatic test code generation
    {
      name: 'interactive-recording',
      testMatch: /.*\.interactive\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }, // Override to desktop Full HD
        headless: false,
        trace: 'off',       // Custom fixture handles recording
        screenshot: 'off',  // Custom fixture handles screenshots
        video: 'off',       // Custom fixture handles video-like recording
        launchOptions: {
          slowMo: 100, // Slow down by 100ms for better observation
        },
      },
      dependencies: ['setup'],
    },

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'cd .. && ./scripts/dev.sh',
    url: 'http://localhost:8000',
    reuseExistingServer: !process.env.CI,
    timeout: 180 * 1000, // 3 minutes: 30s backend + 30s Next.js + buffer
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
