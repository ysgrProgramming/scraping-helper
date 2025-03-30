from __future__ import annotations

import datetime
import time

from pydantic import BaseModel, Field, PrivateAttr
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .slack_notificater import SlackNotificater


class AutoDriver(BaseModel):
    min_interval: float = Field(default=1.0, ge=0)
    retry_count: int = Field(default=3, ge=0)
    timeout: int = Field(default=10, ge=0)
    error_notificater: SlackNotificater | None = Field(default=None)
    fatal_notificater: SlackNotificater | None = Field(default=None)
    _driver: webdriver.Chrome = PrivateAttr()
    _last_get_time: datetime.datetime = PrivateAttr(default=datetime.datetime.min)

    def model_post_init(self, __context: dict, /) -> None:
        self._driver = create_driver()
        return super().model_post_init(__context)

    def safe_get(self, url: str, retries: int = 3, timeout: int = 10) -> str:
        """WebDriverWait とリトライ処理を用いて指定 URL のページ取得を行う汎用関数"""
        for attempt in range(retries + 1):
            try:
                now = datetime.datetime.now()
                elapsed = now - self._last_get_time
                if elapsed < self.min_interval:
                    time.sleep(self.min_interval - elapsed)
                self._last_get_time = now
                self._driver.get(url)
                self._driver.set_page_load_timeout(timeout)
                WebDriverWait(self._driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body")),
                )
                return self._driver.page_source  # noqa: TRY300

            except WebDriverException as e:  # noqa: PERF203
                self.error_notificater.notify(
                    f"エラー起きとるわ。: Attempt {attempt} failed for {url}: {e}",
                )
                print(f"Attempt {attempt} failed for {url}: {e}")
                self._driver.quit()
                self._driver = create_driver()
                time.sleep(2)
        self.fatal_notificater.notify("無理くせえわ。終了するで。")
        msg = f"Failed to get {url} after {retries} attempts"
        raise WebDriverException(
            msg,
        )

    def quit(self) -> None:
        self._driver.quit()


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
    return driver
