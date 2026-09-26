"""Optional UI regression check: python tests/browser_journey.py (Playwright + Edge)."""
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".runtime/browser-tools"))
from playwright.sync_api import sync_playwright
from app import make_handler
from marketlens.service import Service


def main():
    (ROOT / ".runtime").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        service = Service(ROOT / "data/prices.csv", Path(folder) / "browser.sqlite3")
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(service))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="msedge", headless=True)
                page = browser.new_page(viewport={"width": 1440, "height": 1100})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                base = f"http://127.0.0.1:{server.server_port}"
                page.goto(base)
                page.wait_for_selector("#onboarding")
                page.screenshot(path=str(ROOT / ".runtime/journey-welcome.png"), full_page=True)
                page.locator("#wizard-next").click()
                assert page.locator("#wizard-error").is_visible()
                page.locator('[name="goal"][value="learn"]').check()
                page.locator('[name="topics"][value="stocks"]').check()
                page.locator("#wizard-next").click()
                page.locator('[name="level"][value="beginner"]').check()
                page.locator("#wizard-next").click()
                page.locator('[name="risk"][value="adventurous"]').check()
                page.locator('[name="horizon"]').select_option("long")
                page.locator("#wizard-back").click()
                assert page.locator('[name="level"][value="beginner"]').is_checked()
                page.locator("#wizard-next").click()
                assert page.locator('[name="risk"][value="adventurous"]').is_checked()
                page.locator("#wizard-next").click()
                page.wait_for_selector("#discover")
                assert "Start with understanding." in page.locator("#discover").inner_text()
                assert page.locator('#discover .suggested [data-mix="Growth"]').count() == 1
                assert "Build your foundations" in page.locator("#discover").inner_text()
                page.screenshot(path=str(ROOT / ".runtime/journey-discover.png"), full_page=True)

                page.locator('[data-page="learn"]').click()
                assert page.locator("#lesson-grid .content-card").count() == 9
                page.locator("#lesson-search").fill("bond")
                assert 0 < page.locator("#lesson-grid .content-card").count() < 9
                page.locator("#lesson-search").fill("not-a-real-topic")
                assert page.locator(".empty-library").is_visible()
                page.locator('[data-clear-filters]').click()
                page.locator("#lesson-topic").select_option("bonds")
                assert page.locator("#lesson-grid .content-card").count() == 1
                page.locator('#lesson-grid [data-save="bonds"]').click()
                page.locator("#saved-only").check()
                assert page.locator("#lesson-grid .content-card").count() == 1
                page.locator('#lesson-grid [data-article="bonds"]').click()
                assert page.locator("#reader").is_visible()
                assert page.locator("#reader a").get_attribute("href").startswith("https://www.finra.org/")
                page.locator('[data-complete="bonds"]').click()
                assert page.locator('[data-complete="bonds"]').inner_text() == "Completed ✓"
                page.keyboard.press("Escape")
                assert not page.locator("#reader").is_visible()
                page.reload()
                page.wait_for_selector("#discover")
                assert "1 saved for later" in page.locator("#discover").inner_text()
                assert page.locator(".progress-number").inner_text().startswith("1")
                page.locator('[data-saved-library]').click()
                assert page.locator("#saved-only").is_checked()
                assert page.locator("#lesson-grid .content-card").count() == 1
                page.locator("#saved-only").uncheck()

                page.locator('[data-page="strategies"]').click()
                assert page.locator("#strategies .mix-card").count() == 3
                assert "simulation not available" in page.locator("#strategies").inner_text()
                page.screenshot(path=str(ROOT / ".runtime/journey-strategies.png"), full_page=True)
                page.locator('#strategies [data-mix="Growth"]').click()
                assert page.locator("#profile").input_value() == "Growth"
                page.locator("#invest").click()
                page.wait_for_selector(".portfolio-value")
                assert service.snapshot()["portfolio"]["profile"] == "Growth"
                for _ in range(5):
                    with page.expect_response("**/api/advance"):
                        page.locator("#advance").click()
                    page.wait_for_function('!document.getElementById("advance").disabled')
                page.locator('[data-page="history"]').click()
                assert service.snapshot()["performance"]["evaluated"] == 3
                page.locator('[data-page="strategies"]').click()
                page.locator('#strategies [data-mix="Conservative"]').click()
                assert "holdings have not changed" in page.locator("#practice-notice").inner_text()
                assert service.snapshot()["portfolio"]["profile"] == "Growth"

                page.locator("#edit-journey").click()
                page.locator('[name="goal"][value="explore"]').check()
                page.locator("#wizard-next").click()
                page.locator('[name="level"][value="advanced"]').check()
                page.locator("#wizard-next").click()
                page.locator('[name="horizon"]').select_option("short")
                page.locator("#wizard-next").click()
                assert "Curiosity is a good starting point" in page.locator("#discover").inner_text()
                assert page.locator("#discover .suggested").count() == 0
                assert "Start with your time horizon" in page.locator("#discover").inner_text()
                assert service.snapshot()["portfolio"]["profile"] == "Growth"
                page.locator("#edit-journey").click()
                page.locator('[name="goal"][value="practice"]').check()
                page.locator("#wizard-next").click()
                page.locator("#wizard-next").click()
                page.locator('[name="risk"][value="cautious"]').check()
                page.locator('[name="horizon"]').select_option("medium")
                page.locator("#wizard-next").click()
                assert "Give your ideas a practice run" in page.locator("#discover").inner_text()
                assert page.locator('#discover .suggested [data-mix="Conservative"]').count() == 1

                page.set_viewport_size({"width": 390, "height": 844})
                for name in ("discover", "learn", "strategies", "markets", "overview", "history"):
                    page.locator(f'[data-page="{name}"]').click()
                    assert page.locator(f"#{name}").is_visible()
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), name
                page.locator('[data-page="discover"]').click()
                page.screenshot(path=str(ROOT / ".runtime/journey-mobile.png"), full_page=True)
                page.locator("#edit-journey").click()
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                page.locator("#wizard-cancel").click()
                assert page.locator("#discover").is_visible()
                page.locator('[data-page="learn"]').click()
                page.locator("#lesson-topic").select_option("all")
                page.locator('#lesson-grid [data-article="risk"]').click()
                assert page.locator("#reader").evaluate("e => e.scrollWidth <= e.clientWidth")
                page.keyboard.press("Escape")

                # Invalid persisted preferences must not bypass onboarding.
                page.evaluate("localStorage.setItem('marketlens.journey.v1', '{broken')")
                page.reload()
                page.wait_for_selector("#onboarding")
                assert not page.locator("#workspace").is_visible()
                assert not errors, errors
                browser.close()
                print("PASS: onboarding validation/back, separate level/risk, all goal routes, short horizon, search/filter/save/read persistence, portfolio handoff, replay, portfolio preservation, mobile pages, dialog, invalid storage; no JS errors.")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    main()
