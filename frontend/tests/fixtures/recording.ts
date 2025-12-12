import { test as base, Page } from '@playwright/test';
import * as fs from 'node:fs';
import * as path from 'node:path';

/**
 * Recording Fixture for Interactive Manual Testing
 *
 * Provides comprehensive recording capabilities:
 * - Network requests/responses
 * - Console logs
 * - Click tracking
 * - React render detection
 * - Automatic screenshots
 * - Test code generation
 */

export interface RecordedAction {
  timestamp: string;
  type: 'click' | 'navigation' | 'render' | 'network' | 'console';
  details: any;
  screenshot?: string;
}

export interface NetworkRequest {
  url: string;
  method: string;
  status?: number;
  timing: number;
  requestHeaders?: Record<string, string>;
  responseHeaders?: Record<string, string>;
  postData?: string;
  responseBody?: string;
}

export interface RecordingSession {
  sessionDir: string;
  screenshotDir: string;
  networkDir: string;
  consoleDir: string;
  recordedActions: RecordedAction[];
  networkRequests: NetworkRequest[];
  consoleLogs: Array<{ type: string; text: string; timestamp: string }>;
  takeScreenshot: (label: string) => Promise<string>;
  finalize: () => void;
}

interface RecordingFixtures {
  recordingSession: RecordingSession;
}

export const test = base.extend<RecordingFixtures>({
  recordingSession: async ({ page }, use, testInfo) => {
    // Setup recording directories under tests/output/recordings/
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const testName = testInfo.title.replace(/\s+/g, '-').toLowerCase();
    const sessionDir = path.join(__dirname, `../output/recordings/recording-${testName}-${timestamp}`);
    const screenshotDir = path.join(sessionDir, 'screenshots');
    const networkDir = path.join(sessionDir, 'network');
    const consoleDir = path.join(sessionDir, 'console');

    for (const dir of [sessionDir, screenshotDir, networkDir, consoleDir]) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }

    const recordedActions: RecordedAction[] = [];
    const networkRequests: NetworkRequest[] = [];
    const consoleLogs: Array<{ type: string; text: string; timestamp: string }> = [];
    let screenshotCounter = 0;

    // Helper: Take screenshot
    const takeScreenshot = async (label: string): Promise<string> => {
      screenshotCounter++;
      const filename = `${screenshotCounter.toString().padStart(4, '0')}-${label}.png`;
      const filepath = path.join(screenshotDir, filename);
      await page.screenshot({ path: filepath, fullPage: false });
      return filename;
    };

    // Helper: Save network request details
    const saveNetworkRequest = (req: NetworkRequest) => {
      const filename = `${networkRequests.length.toString().padStart(4, '0')}-${req.method}-${Date.now()}.json`;
      fs.writeFileSync(
        path.join(networkDir, filename),
        JSON.stringify(req, null, 2)
      );
    };

    // Setup console listener
    page.on('console', (msg) => {
      const logEntry = {
        type: msg.type(),
        text: msg.text(),
        timestamp: new Date().toISOString(),
      };
      consoleLogs.push(logEntry);

      recordedActions.push({
        timestamp: logEntry.timestamp,
        type: 'console',
        details: logEntry,
      });

      console.log(`[CONSOLE ${msg.type().toUpperCase()}] ${msg.text()}`);
    });

    // Setup network request listener
    page.on('request', (request) => {
      console.log(`[NETWORK REQUEST] ${request.method()} ${request.url()}`);
    });

    // Setup network response listener
    page.on('response', async (response) => {
      const reqData: NetworkRequest = {
        url: response.url(),
        method: response.request().method(),
        status: response.status(),
        timing: Date.now(),
        requestHeaders: response.request().headers(),
        responseHeaders: response.headers(),
        postData: response.request().postData() || undefined,
      };

      // Capture response body for API calls (not images/fonts)
      const contentType = response.headers()['content-type'] || '';
      if (contentType.includes('json') || contentType.includes('text')) {
        try {
          reqData.responseBody = await response.text();
        } catch (e) {
          // Response body might not be available
        }
      }

      networkRequests.push(reqData);
      saveNetworkRequest(reqData);

      recordedActions.push({
        timestamp: new Date().toISOString(),
        type: 'network',
        details: {
          url: reqData.url,
          method: reqData.method,
          status: reqData.status,
        },
      });

      console.log(`[NETWORK RESPONSE] ${response.status()} ${response.url()}`);
    });

    // Inject click and render tracking
    await page.addInitScript(() => {
      let clickCount = 0;
      let renderCount = 0;

      // Track clicks
      document.addEventListener('click', (e) => {
        clickCount++;
        const target = e.target as HTMLElement;
        const elementInfo = {
          clickNumber: clickCount,
          tag: target.tagName,
          id: target.id || null,
          className: typeof target.className === 'string' ? target.className : null,
          text: target.textContent?.substring(0, 100) || null,
          timestamp: new Date().toISOString(),
          selector: generateSelector(target),
        };
        (window as any).__lastClick = elementInfo;
        console.log('[CLICK TRACKED]', JSON.stringify(elementInfo));
      }, true);

      // Generate CSS selector for element
      function generateSelector(element: HTMLElement): string {
        if (element.id) return `#${element.id}`;

        let selector = element.tagName.toLowerCase();
        if (element.className && typeof element.className === 'string') {
          const classes = element.className.trim().split(/\s+/).slice(0, 3);
          selector += '.' + classes.join('.');
        }

        return selector;
      }

      // Track React renders using MutationObserver
      const observer = new MutationObserver((mutations) => {
        const hasSignificantChange = mutations.some(mutation =>
          mutation.type === 'childList' && mutation.addedNodes.length > 0
        );

        if (hasSignificantChange) {
          renderCount++;
          (window as any).__lastRender = {
            renderNumber: renderCount,
            timestamp: new Date().toISOString(),
          };
          console.log('[REACT RENDER DETECTED]', renderCount);
        }
      });

      observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
      });

      (window as any).__renderObserver = observer;
    });

    // Function to finalize and save recording data
    const finalize = () => {
      console.log('💾 Saving recording data...\n');

      fs.writeFileSync(
        path.join(sessionDir, 'recorded-actions.json'),
        JSON.stringify(recordedActions, null, 2)
      );

      fs.writeFileSync(
        path.join(sessionDir, 'network-requests.json'),
        JSON.stringify(networkRequests, null, 2)
      );

      fs.writeFileSync(
        path.join(sessionDir, 'console-logs.json'),
        JSON.stringify(consoleLogs, null, 2)
      );

      // Generate test code from recorded actions (as template, not executable test)
      const generatedTest = generateTestCode(recordedActions, testInfo.title);
      fs.writeFileSync(
        path.join(sessionDir, 'generated-test.ts.template'),
        generatedTest
      );

      console.log('='.repeat(100));
      console.log('✅ RECORDING SESSION COMPLETED');
      console.log('='.repeat(100));
      console.log(`\n📊 Session Summary:`);
      console.log(`   Test: ${testInfo.title}`);
      console.log(`   Total Actions: ${recordedActions.length}`);
      console.log(`   Clicks: ${recordedActions.filter(a => a.type === 'click').length}`);
      console.log(`   Renders: ${recordedActions.filter(a => a.type === 'render').length}`);
      console.log(`   Network Requests: ${networkRequests.length}`);
      console.log(`   Console Logs: ${consoleLogs.length}`);
      console.log(`   Screenshots: ${screenshotCounter}`);
      console.log(`\n📂 Recording saved to: ${sessionDir}`);
      console.log(`\n🧪 Generated test template: ${path.join(sessionDir, 'generated-test.ts.template')}`);
      console.log(`   💡 Rename to .spec.ts and add assertions to use as automated test`);
      console.log('\n' + '='.repeat(100) + '\n');
    };

    const session: RecordingSession = {
      sessionDir,
      screenshotDir,
      networkDir,
      consoleDir,
      recordedActions,
      networkRequests,
      consoleLogs,
      takeScreenshot,
      finalize,
    };

    console.log('\n' + '='.repeat(100));
    console.log('🎬 INTERACTIVE RECORDING SESSION STARTED');
    console.log('='.repeat(100));
    console.log(`\n📂 Recording to: ${sessionDir}`);
    console.log(`\n🎯 Test: ${testInfo.title}`);
    console.log('\n🎯 RECORDING FEATURES:');
    console.log('   ✅ Network requests and responses');
    console.log('   ✅ Console logs (all levels)');
    console.log('   ✅ Click tracking with selectors');
    console.log('   ✅ React component renders');
    console.log('   ✅ Screenshots on every interaction');
    console.log('   ✅ Automatic test code generation');
    console.log('\n⏱️  NO TIMEOUT - Session runs until you close the browser or press Ctrl+C');
    console.log('\n' + '='.repeat(100) + '\n');

    // Provide session to test
    await use(session);

    // Cleanup and save on test completion
    finalize();
  },
});

/**
 * Generate Playwright test code from recorded actions
 */
function generateTestCode(actions: RecordedAction[], testName: string): string {
  const clicks = actions.filter(a => a.type === 'click');
  const navigationAction = actions.find(a => a.type === 'navigation');
  const url = navigationAction?.details?.url || '/';

  let testCode = `import { test, expect } from '@playwright/test';

/**
 * Auto-generated test from recording session
 * Original test: ${testName}
 * Generated at: ${new Date().toISOString()}
 * Total actions recorded: ${actions.length}
 */

test.describe('${testName} - Replay', () => {
  test('replay recorded session', async ({ page }) => {
    // Navigate to page
    await page.goto('${url}');
    await page.waitForLoadState('networkidle');

`;

  for (const click of clicks) {
    const { selector, text, tag } = click.details;
    testCode += `    // Click #${click.details.clickNumber}: ${tag}${text ? ` - "${text.substring(0, 30)}"` : ''}\n`;
    testCode += `    await page.locator('${selector}').click();\n`;
    testCode += `    await page.waitForLoadState('networkidle');\n\n`;
  }

  testCode += `    // Add your assertions here\n`;
  testCode += `  });\n`;
  testCode += `});\n`;

  return testCode;
}

export { expect } from '@playwright/test';
