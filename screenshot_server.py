from flask import Flask, request, send_file, jsonify
import asyncio
from playwright.async_api import async_playwright
import os
from urllib.parse import quote_plus

app = Flask(__name__)
SCREENSHOT_DIR = './screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

@app.route('/screenshot')
def screenshot():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    filename = quote_plus(url) + ".png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    if not os.path.exists(filepath):
        try:
            asyncio.run(take_screenshot(url, filepath))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return send_file(filepath, mimetype='image/png')

async def take_screenshot(url, path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
        )
        page = await context.new_page()

        await page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com"
        })

        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.screenshot(path=path, full_page=False)

        await browser.close()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))  # ✅ required for Render
    app.run(host='0.0.0.0', port=port)         # ✅ 0.0.0.0 is required for public access
