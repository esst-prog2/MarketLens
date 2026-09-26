"""Offline MVP/class walkthrough in headless Edge; python tests/browser_mvp.py."""
from datetime import timedelta
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/".runtime/browser-tools"))
from playwright.sync_api import sync_playwright
from app import make_handler
from test_mvp import FakeProvider
from marketlens.mvp import MVPService


def main():
    with tempfile.TemporaryDirectory() as folder, patch("urllib.request.urlopen",side_effect=AssertionError("Offline browser test")):
        provider=FakeProvider(); clock=[provider.observed]
        s=MVPService(ROOT/"data/training_prices.csv",Path(folder)/"browser.sqlite3",provider,lambda:clock[0])
        server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(s))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(channel="msedge",headless=True)
                page=browser.new_page(viewport={"width":1440,"height":1100})
                errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
                page.goto(f"http://127.0.0.1:{server.server_port}")
                page.locator('[name="goal"][value="practice"]').check()
                page.locator('[name="topics"][value="stocks"]').check()
                page.locator('#wizard-next').click()
                page.locator('[name="level"][value="beginner"]').check()
                page.locator('#wizard-next').click()
                page.locator('[name="risk"][value="balanced"]').check()
                page.locator('[name="horizon"]').select_option('long')
                page.locator('#wizard-next').click()
                page.locator('[data-page="overview"]').click()
                page.wait_for_function('state?.mode === "current" && !busy')
                assert page.locator('#signals .market-card').count()==3
                assert page.locator('#invest').is_disabled()
                assert 'Unavailable' in page.locator('#signals').inner_text()
                s.refresh()
                page.locator('#refresh').click()
                page.wait_for_function('state.can_invest && !busy')
                assert page.locator('#signals .forecast').count()==6
                assert 'probability' in page.locator('#signals').inner_text()
                page.locator('#invest').click()
                page.wait_for_selector('.portfolio-value')
                assert s.snapshot()['portfolio']['value']==10000
                clock[0]+=timedelta(minutes=5);provider.observed=clock[0];provider.price['SPY']=110;s.refresh()
                page.locator('#refresh').click()
                page.wait_for_function('state.portfolio.value === 10500 && !busy')
                provider.fail=True;clock[0]+=timedelta(minutes=31);s.refresh()
                page.locator('#refresh').click()
                page.wait_for_function('!state.portfolio.fresh && !busy')
                assert 'provider error' in page.locator('#provider-status').inner_text()
                assert 'Cached' in page.locator('#portfolio').inner_text()
                current_holdings=s.snapshot()['portfolio']['holdings']
                page.locator('[data-page="learn"]').click()
                page.locator('#lesson-grid [data-save="bonds"]').click()
                preferences=page.evaluate('JSON.stringify(localStorage)')
                page.locator('#data-mode').select_option('replay')
                page.wait_for_function('state.mode === "replay" && !busy')
                page.locator('[data-page="overview"]').click()
                page.locator('#invest').click();page.wait_for_function('!!state.portfolio && !busy')
                calls=provider.calls
                for _ in range(26):
                    page.locator('#advance').click()
                    page.wait_for_function('!busy')
                assert provider.calls==calls
                page.locator('[data-page="history"]').click()
                assert page.locator('.comparison[data-status="complete"]').count()>0
                assert 'Incorrect' in page.locator('#history-rows').inner_text()
                page.locator('.comparison[data-status="complete"] summary').first.click()
                page.screenshot(path=str(ROOT/'.runtime/mvp-history.png'),full_page=True)
                page.locator('#metric-version').select_option(index=1)
                assert 'Brier' in page.locator('#reliability').inner_text()
                page.set_viewport_size({"width":390,"height":844})
                for name in ('discover','learn','strategies','markets','overview','history'):
                    page.locator(f'[data-page="{name}"]').click()
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),name
                page.locator('[data-page="overview"]').click()
                page.screenshot(path=str(ROOT/'.runtime/mvp-mobile.png'),full_page=True)
                page.on('dialog',lambda d:d.accept())
                page.locator('#reset').click()
                page.wait_for_function('!state.portfolio && !busy')
                assert page.evaluate('JSON.stringify(localStorage)')==preferences
                page.locator('#data-mode').select_option('current')
                page.wait_for_function('state.mode === "current" && !busy')
                assert s.snapshot()['portfolio']['holdings']==current_holdings
                assert not errors,errors
                browser.close()
                replay=s.snapshot('replay')
                print('PASS: offline current-data fixtures, unavailable/price change/outage, two targets, 26-session replay retraining, complete frozen cohort, mistakes, version metrics, saved preferences, isolated reset, desktop and 390px; no JS errors.')
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__=='__main__':main()
