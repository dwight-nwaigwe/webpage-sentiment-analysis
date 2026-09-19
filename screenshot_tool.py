# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 09:05:55 2026

@author: dwight
"""

import sys
import asyncio
from threading import Thread
from playwright.async_api import async_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def _worker_screenshot(url, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # CHANGED: "domcontentloaded" stops tracking infinite network requests
        print("Navigating to target page...")
        await page.goto(url, wait_until="domcontentloaded")
        
        # OPTIONAL: Give complex visual layouts a couple of seconds to settle 
        # before snapping the frame
        await asyncio.sleep(3)
        
        
        #accept cookies or whatever appears so that the website homepage can be
        #fully seen
        accept_button = page.get_by_role(
            "button",
            name=r"(Accept|Allow|I agree|Got it|Accept all|Accept cookies)",
            exact=False,
        )

        try:
            # Wait up to 3 seconds for the button to appear and click it
            await accept_button.first.click(timeout=3000)
            print("Accepted banner standard dialog!")
        except Exception:
            print("No agreement banner appeared.")

       
        
        
        
        print("Capturing full page screenshot...")
        await page.screenshot(path=output_path, full_page=True)
        
        await browser.close()
        print(f"File successfully created: {output_path}")

def take_screenshot_isolated(url, output_path):
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_worker_screenshot(url, output_path))
        loop.close()

    thread = Thread(target=run_in_thread)
    thread.start()
    thread.join()




