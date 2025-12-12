import { test, expect } from './fixtures/recording';

/**
 * Intelligence Agent Interactive Recording Test
 *
 * Uses the recording fixture to capture all interactions with the intelligence agent display page.
 * No timeout - runs until browser is closed manually.
 */

test.describe('Intelligence Agent Interactive Recording', () => {
  test('record intelligence agent manual testing session', async ({ page, recordingSession }) => {
    // Very long timeout (1 hour) but not infinite - prevents runaway tests
    test.setTimeout(60 * 60 * 1000);

    // Navigate to intelligence agent page
    console.log('🌐 Navigating to intelligence agent page...');
    try {
      await page.goto('/?page=display&type=intelligence_agent', { waitUntil: 'domcontentloaded' });
      console.log('✅ Page loaded (DOM ready)');
    } catch (error) {
      console.log(`\n🛑 Browser closed during navigation: ${error instanceof Error ? error.message : 'unknown error'}\n`);
      return; // Exit gracefully
    }

    // Wait for component to render completely (Synthesizer heading is the last section)
    console.log('⏳ Waiting for component to render...');
    try {
      // Wait for Synthesizer heading to ensure component is fully rendered
      await page.getByRole('heading', { name: 'Synthesizer' }).waitFor({ state: 'visible', timeout: 10000 });
      console.log('✅ Synthesizer heading found - component fully rendered');     

      // Wait for render to complete
      await page.waitForTimeout(500);
      console.log('✅ WebGL render complete');
    } catch (error) {
      console.log('\n🛑 Browser closed or Intelligence Agent failed to load\n');
      return; // Exit gracefully
    }

    // Take initial screenshot (handle WebGL timing issues gracefully)
    let initialScreenshot: string = '';
    try {
      initialScreenshot = await recordingSession.takeScreenshot('agent-message-loaded');
      console.log('✅ Initial screenshot captured');
    } catch (error) {
      console.log('\n⚠️  Screenshot failed  - continuing anyway\n');
      initialScreenshot = 'FAILED-timing-issue';
    }

    // ALWAYS add navigation action, even if screenshot failed
    recordingSession.recordedActions.push({
      timestamp: new Date().toISOString(),
      type: 'navigation',
      details: { url: '/?page=display&type=intelligence_agent', action: 'intelligence_agent_load' },
      screenshot: initialScreenshot,
    });

    console.log('✅ Intelligence Agent loaded - ready for manual testing\n');
    console.log('👀 Monitoring for user interactions...\n');

    // Helper to safely check page status
    async function isPageAlive(): Promise<boolean> {
      if (page.isClosed()) return false;

      try {
        await page.evaluate(() => true);
        return true;
      } catch {
        return false;
      }
    }

    // Monitor for interactions
    let lastClickCount = 0;
    let lastRenderCount = 0;
    const checkInterval = 500;

    while (await isPageAlive()) {
      try {
        await page.waitForTimeout(checkInterval);
      } catch {
        // Browser closed during wait
        break;
      }

      // Check for clicks (no try/catch needed - isPageAlive handles it)
      const clickInfo = await page.evaluate(() => (window as any).__lastClick).catch(() => null);
      if (clickInfo && clickInfo.clickNumber > lastClickCount) {
        console.log(`\n🖱️  CLICK #${clickInfo.clickNumber} DETECTED`);
        console.log(`   Element: <${clickInfo.tag}>`);
        console.log(`   Selector: ${clickInfo.selector}`);
        if (clickInfo.id) console.log(`   ID: ${clickInfo.id}`);
        if (clickInfo.text) console.log(`   Text: ${clickInfo.text.substring(0, 50)}`);

        await page.waitForTimeout(1000);

      

        let screenshot = '';
        try {
          screenshot = await recordingSession.takeScreenshot(`click-${clickInfo.clickNumber}`);
        } catch {
          console.log(`   ⚠️  Screenshot failed for click ${clickInfo.clickNumber} - continuing anyway`);
          screenshot = 'FAILED-timing-issue';
        }

        recordingSession.recordedActions.push({
          timestamp: clickInfo.timestamp,
          type: 'click',
          details: clickInfo,
          screenshot,
        });

        lastClickCount = clickInfo.clickNumber;
        console.log(`   📸 Screenshot: ${screenshot}\n`);
      }

      // Check for renders
      const renderInfo = await page.evaluate(() => (window as any).__lastRender).catch(() => null);
      if (renderInfo && renderInfo.renderNumber > lastRenderCount) {
        console.log(`\n⚛️  REACT RENDER #${renderInfo.renderNumber} DETECTED`);

        await page.waitForTimeout(200);

        let screenshot = '';
        try {
          screenshot = await recordingSession.takeScreenshot(`render-${renderInfo.renderNumber}`);
        } catch {
          console.log(`   ⚠️  Screenshot failed for render ${renderInfo.renderNumber} - continuing anyway`);
          screenshot = 'FAILED-timing-issue';
        }

        recordingSession.recordedActions.push({
          timestamp: renderInfo.timestamp,
          type: 'render',
          details: renderInfo,
          screenshot,
        });

        lastRenderCount = renderInfo.renderNumber;
        console.log(`   📸 Screenshot: ${screenshot}\n`);
      }
    }

    console.log('\n🛑 Browser closed - ending session\n');
  });
});
