import { test, expect } from './fixtures/recording';

/**
 * Mapbox Interactive Recording Test
 *
 * Uses the recording fixture to capture all interactions with the mapbox display page.
 * No timeout - runs until browser is closed manually.
 */

test.describe('Mapbox Interactive Recording', () => {
  test('record mapbox manual testing session', async ({ page, recordingSession }) => {
    // Very long timeout (1 hour) but not infinite - prevents runaway tests
    test.setTimeout(60 * 60 * 1000);

    // Navigate to mapbox page
    console.log('🌐 Navigating to mapbox page...');
    try {
      await page.goto('/?page=display&type=mapbox', { waitUntil: 'domcontentloaded' });
      console.log('✅ Page loaded (DOM ready)');
    } catch (error) {
      console.log(`\n🛑 Browser closed during navigation: ${error instanceof Error ? error.message : 'unknown error'}\n`);
      return; // Exit gracefully
    }

    // Wait for mapbox to render (WebGL initialization takes longer than standard canvas)
    console.log('⏳ Waiting for mapbox to render...');
    try {
      // Wait for Mapbox canvas to exist
      await page.waitForSelector('.mapboxgl-canvas', { state: 'attached', timeout: 10000 });
      console.log('✅ Mapbox canvas found');

      // Wait for Mapbox 'load' event to ensure map is fully initialized
      await page.evaluate(() => {
        return new Promise((resolve) => {
          const checkMap = () => {
            const mapInstance = (window as any).mapboxMap;
            if (mapInstance && mapInstance.loaded()) {
              resolve(true);
            } else {
              setTimeout(checkMap, 100);
            }
          };
          checkMap();
        });
      });
      console.log('✅ Mapbox map loaded event fired');

      // Trigger a repaint to ensure canvas buffer is ready
      await page.evaluate(() => {
        const mapInstance = (window as any).mapboxMap;
        if (mapInstance && mapInstance.triggerRepaint) {
          mapInstance.triggerRepaint();
        }
      });

      // Wait for render to complete
      await page.waitForTimeout(500);
      console.log('✅ WebGL render complete');
    } catch (error) {
      console.log('\n🛑 Browser closed or Mapbox failed to load\n');
      return; // Exit gracefully
    }

    // Take initial screenshot (handle WebGL timing issues gracefully)
    let initialScreenshot: string = '';
    try {
      initialScreenshot = await recordingSession.takeScreenshot('mapbox-loaded');
      console.log('✅ Initial screenshot captured');
    } catch (error) {
      console.log('\n⚠️  Screenshot failed (WebGL timing issue) - continuing anyway\n');
      initialScreenshot = 'FAILED-webgl-timing-issue';
    }

    // ALWAYS add navigation action, even if screenshot failed
    recordingSession.recordedActions.push({
      timestamp: new Date().toISOString(),
      type: 'navigation',
      details: { url: '/?page=display&type=mapbox', action: 'mapbox_load' },
      screenshot: initialScreenshot,
    });

    console.log('✅ Mapbox loaded - ready for manual testing\n');
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

        // Trigger repaint before screenshot to ensure WebGL buffer is ready
        await page.evaluate(() => {
          const mapInstance = (window as any).mapboxMap;
          if (mapInstance && mapInstance.triggerRepaint) {
            mapInstance.triggerRepaint();
          }
        }).catch(() => {});
        await page.waitForTimeout(200);

        let screenshot = '';
        try {
          screenshot = await recordingSession.takeScreenshot(`click-${clickInfo.clickNumber}`);
        } catch {
          console.log(`   ⚠️  Screenshot failed for click ${clickInfo.clickNumber} - continuing anyway`);
          screenshot = 'FAILED-webgl-timing-issue';
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

        // Trigger repaint before screenshot to ensure WebGL buffer is ready
        await page.evaluate(() => {
          const mapInstance = (window as any).mapboxMap;
          if (mapInstance && mapInstance.triggerRepaint) {
            mapInstance.triggerRepaint();
          }
        }).catch(() => {});
        await page.waitForTimeout(200);

        let screenshot = '';
        try {
          screenshot = await recordingSession.takeScreenshot(`render-${renderInfo.renderNumber}`);
        } catch {
          console.log(`   ⚠️  Screenshot failed for render ${renderInfo.renderNumber} - continuing anyway`);
          screenshot = 'FAILED-webgl-timing-issue';
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
