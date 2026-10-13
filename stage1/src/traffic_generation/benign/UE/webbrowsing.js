import puppeteer from 'puppeteer';

// ----------- Functions -----------
// Simulates user reading content of website
function wait(ms) {
  console.log(`User on website for ${(ms).toFixed(2)/1000} seconds`);
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Get random integer
function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Reading Time (1 - 10 minutes)
function timeOnTab(){
  return randomInt(1000*60, 1000*60*10);
}

// Amount of tabs the user will open
function amountTabsOpen(){
  return randomInt(1,5);
}

// ----------- Start of Script -----------
// Define constant time-values
const startTime = Date.now();
const fourHours = 4 * 60 * 60 * 1000;
const endTime = startTime + fourHours;

// Loop until predefined time is passed
while (Date.now() < endTime) {
  const numTabsFinal = amountTabsOpen(); // Get random number of tabs for this round (1 - 5 tabs)
  console.log(`User will use ${numTabsFinal} tabs`);
  var numTabs = 0;

  // Launch the browser and open a new blank page
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });
  const page = await browser.newPage();
  // Visit webpage with url pointing to webserver
  await page.goto('http://192.168.3.3', {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  });
  console.log('On website!');
  await page.setViewport({width: 1080, height: 1024});
  await wait(timeOnTab()); // User is reading (1 - 10 min)...
  numTabs++;

  // Read through predefined random number of tabs
  while (numTabs < numTabsFinal && Date.now() < endTime){
    const page = await browser.newPage();

    // Navigate the page to webserver
    await page.goto('https://192.168.3.3/');
    console.log('On website!')

    await page.setViewport({width: 1080, height: 1024});
    await wait(timeOnTab()); // User is reading (1 - 10 min)...
    numTabs++;
  }
  // Close all tabs/browser when finished reading for this round
  await browser.close();
}
