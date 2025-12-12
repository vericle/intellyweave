import path from 'node:path';
import { test as setup } from '@playwright/test';

/**
 * Authentication Setup for Playwright Tests
 *
 * This setup script runs before all tests to configure the browser session
 * with necessary local storage settings to bypass configuration screens.
 *
 * The storage state is saved to tests/state/storage-state.json and reused
 * across all test sessions.
 */

const storageStatePath = path.join(__dirname, '../state/storage-state.json');

setup('configure application settings', async ({ page }) => {
  // Navigate to the application
  await page.goto('http://localhost:3000');

  // Set all required local storage items to bypass startup dialogs
  await page.evaluate(() => {
    const localStorageSettings = {
      'INTELLYWEAVE_START_DIALOG_DONT_SHOW_AGAIN': 'true',
      'TLDRAW_USER_DATA_v3': JSON.stringify({
        version: 3,
        user: {
          id: 'DbASEZKXfuFjI766An21f',
          isDarkMode: false
        }
      }),
      'mapbox.eventData:ZXVkYWltb25pYXRlY2g=': JSON.stringify({
        lastSuccess: 1763507563098,
        tokenU: 'vericle'
      }),
      'device_id': '6411455e37173aa73261b786be979cfa',
      'mapbox.eventData.uuidTimestamp:ZXVkYWltb25pYXRlY2g=': '1763485142374',
      'jam_ephemeral_events_content-interactivity-events': '[]',
      'mapbox.eventData.uuid:ZXVkYWltb25pYXRlY2g=': '1c5dc1b7-29d8-4157-b7f7-fc0b00ef074c'
    };

    for (const [key, value] of Object.entries(localStorageSettings)) {
      localStorage.setItem(key, value);
    }
  });

  // Verify the settings were applied
  const startDialogSetting = await page.evaluate(() =>
    localStorage.getItem('INTELLYWEAVE_START_DIALOG_DONT_SHOW_AGAIN')
  );

  if (startDialogSetting !== 'true') {
    throw new Error('Failed to set local storage for startup dialog bypass');
  }

  // Save the storage state for reuse in all tests
  await page.context().storageState({ path: storageStatePath });

  console.log('✅ Application settings configured successfully');
  console.log(`📁 Storage state saved to: ${storageStatePath}`);
});
