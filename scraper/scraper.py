#!/usr/bin/env python3
import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass


# --- セキュリティ向上: Slack Webhook URL は環境変数から取得する ---
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
if not SLACK_WEBHOOK_URL:
    raise ValueError("SLACK_WEBHOOK_URL environment variable is not set")

BASE_URL = "https://www.winticket.jp"
DATA_DIR = "datas"


@dataclass
class Scraper:
    driver: webdriver.Chrome | None = None
    last_fetch_date: datetime = datetime.now()
    fetch_interval: datetime.timedelta = timedelta(seconds=1)

    def __post_init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-application-cache")
        options.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=options)

    def safe_get(driver, url, retries=3, timeout=30):
        """
        driver.get(url) をWebDriverWaitとリトライ処理で実行する関数
        """
        for attempt in range(1, retries + 1):
            try:
                driver.set_page_load_timeout(timeout)
                driver.get(url)
                # bodyタグが出現するまで待つ
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return driver.page_source
            except Exception as e:
                print(f"Attempt {attempt} failed for {url}: {e}")
                if attempt == retries:
                    raise
                time.sleep(2)
