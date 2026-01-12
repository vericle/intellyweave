import { test, expect } from './fixtures/recording';

/**
 * Network Chart Interactive Recording Test
 *
 * Uses the recording fixture to capture all interactions with the network chart page.
 * No timeout - runs until browser is closed manually.
 */

test.describe('Network Chart Interactive Recording', () => {
  test('record network chart manual testing session', async ({ page, recordingSession }) => {
    // Very long timeout (1 hour) but not infinite - prevents runaway tests
    test.setTimeout(60 * 60 * 1000);

    // Navigate to network chart page
    console.log('🌐 Navigating to network chart page...');
    try {
      await page.goto('/?page=display&type=network_chart');
      console.log('✅ Page loaded, waiting for network idle...');
      await page.waitForLoadState('networkidle');
      console.log('✅ Network idle');
    } catch (error) {
      console.log(`\n🛑 Browser closed during navigation: ${error instanceof Error ? error.message : 'unknown error'}\n`);
      return; // Exit gracefully
    }

    // Wait for network chart to render
    console.log('⏳ Waiting for network chart to render...');
    try {
      await page.waitForTimeout(5000);
    } catch (error) {
      console.log('\n🛑 Browser closed while waiting for chart to render\n');
      return; // Exit gracefully
    }

    // Take initial screenshot
    let initialScreenshot: string;
    try {
      initialScreenshot = await recordingSession.takeScreenshot('network-chart-loaded');
    } catch (error) {
      console.log('\n🛑 Browser closed during screenshot\n');
      return; // Exit gracefully
    }
    recordingSession.recordedActions.push({
      timestamp: new Date().toISOString(),
      type: 'navigation',
      details: { url: '/?page=display&type=network_chart', action: 'network_chart_load' },
      screenshot: initialScreenshot,
    });

    console.log('✅ Network chart loaded - ready for manual testing\n');
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

        const screenshot = await recordingSession.takeScreenshot(`click-${clickInfo.clickNumber}`);

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

        const screenshot = await recordingSession.takeScreenshot(`render-${renderInfo.renderNumber}`);

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
