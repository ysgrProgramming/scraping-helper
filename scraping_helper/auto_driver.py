import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from pydantic import BaseModel, PrivateAttr
import datetime


class AutoDriver(BaseModel):
    min_interval: float = 1.0
    retry_count: int = 2
    timeout: int = 30

    _driver: webdriver.Chrome = PrivateAttr()
    _last_get_time: datetime.datetime = PrivateAttr(default=datetime.datetime.min)

    def model_post_init(self, __context) -> None:
        self._driver = create_driver()
        return super().model_post_init(__context)

    def safe_get(self, url: str, retries: int = 3, timeout: int = 10) -> str:
        """
        WebDriverWait とリトライ処理を用いて指定 URL のページ取得を行う汎用関数
        """

        for attempt in range(retries + 1):
            try:
                now = datetime.datetime.now()
                elapsed = now - self._last_get_time
                if elapsed < self.min_interval:
                    time.sleep(self.min_interval - elapsed)
                self._driver.get(url)
                self._driver.set_page_load_timeout(timeout)
                WebDriverWait(self._driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self._driver.page_source

            except Exception as e:
                if attempt == retries:
                    # send_slack_notification("無理くせえわ。終了するで。")
                    raise WebDriverException(
                        f"Failed to get {url} after {retries} attempts"
                    )
                # send_slack_notification(
                #     f"エラー起きとるわ。: Attempt {attempt} failed for {url}: {e}"
                # )
                print(f"Attempt {attempt} failed for {url}: {e}")
                self._driver.quit()
                self._driver = create_driver()
                time.sleep(2)

    def quit(self):
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
