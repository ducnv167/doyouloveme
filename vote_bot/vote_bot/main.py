import shutil
import os
import time
import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

from selenium_stealth import stealth

url = "https://api.weyoung.vn/login-gg.htm"
KEYWORDS = ("KINGDOM", "SOOBIN", "ALL-ROUNDERS", "CƯỜNG BẠCH")
BASE_DIR = str(Path.cwd())

parser = argparse.ArgumentParser(description="Vote automation")
parser.add_argument(
    "--file",
    type=str,
    default="account",
    help="Đường dẫn file account CSV"
)
args = parser.parse_args()
if os.path.exists(f"{BASE_DIR}\\{args.file}"):
    shutil.rmtree(f"{BASE_DIR}\\{args.file}")
os.makedirs(
    f"{BASE_DIR}\\{args.file}", exist_ok=True)

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--disable-crash-reporter")
options.add_argument("--disable-oopr-debug-crash-dump")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--window-size=1280,800")
options.add_argument("--log-level=3")
options.add_argument(
    f"--user-data-dir={BASE_DIR}\\{args.file}")
options.add_experimental_option(
    "prefs",
    {
        "signin.allowed_on_next_startup": False
    }
)
driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_script("return navigator.language")
options = webdriver.ChromeOptions()

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        webdriver = False)
        
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {
        "source": """
        (function () {
            const _debugger = window.debugger;
            Object.defineProperty(window, 'debugger', {
                get() { return () => {}; }
            });
        })();
        """
    }
)
wait = WebDriverWait(driver, 30)


def check_singer(css: str) -> bool:
    elems = driver.find_elements(By.CSS_SELECTOR, css)
    if not elems:
        return False

    text = elems[0].text.upper()
    return any(k in text for k in KEYWORDS)


def preload():
    print("PRELOAD")
    driver.get(url)
    i = 0
    while True:
        i += 1
        if i == 5:
            driver.get(url)
        if "accounts.google.com" in driver.current_url:
            return True
        time.sleep(2)
        try:
            try:
                driver.find_element(
                    By.CSS_SELECTOR, "body > div.swal2-container.swal2-center.swal2-fade.swal2-shown > div > div.swal2-actions > button.swal2-confirm.swal2-styled").click()
            except Exception as e:
                driver.find_element(By.ID, "btnCapchaSubmit").click()
        except:
            time.sleep(2)
            checkpoint_1 = driver.find_elements(
                By.CSS_SELECTOR, "#wraptNotLogin")
            if checkpoint_1 and checkpoint_1[0].is_displayed():
                return False

        time.sleep(5)


def login(username, password):
    print("LOGIN")
    # Nhập email
    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    email_input.send_keys(username)
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#identifierNext button"))).click()
    time.sleep(3)
    # Nhập password
    wait.until(
        EC.visibility_of_any_elements_located(
            (By.CSS_SELECTOR, "#password input"))
    )
    password_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#password input"))
    )
    password_input.send_keys(password)
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#passwordNext button"))).click()

    time.sleep(5)
    elems = driver.find_elements(By.ID, "confirm")
    if elems:
        elem = elems[0]
        wait.until(EC.element_to_be_clickable(elem))
        elem.click()
        time.sleep(3)
        elems_1 = driver.find_elements(
            By.CSS_SELECTOR, "#yDmH0d > c-wiz > main > div.JYXaTc.F8PBrb > div > div > div:nth-child(2) > div > div > button > span")
        if elems_1:
            elem_1 = elems_1[0]
            wait.until(EC.element_to_be_clickable(elem_1))
            elem_1.click()
    elems = driver.find_elements(By.CSS_SELECTOR, "#gaplustosNext > div > button > span")
    if elems:
        scroll_to_y(3000)
        elem = elems[0]
        wait.until(EC.element_to_be_clickable(elem))
        elem.click()
        time.sleep(3)
        elems_1 = driver.find_elements(
            By.CSS_SELECTOR, "#yDmH0d > c-wiz > main > div.JYXaTc.F8PBrb > div > div > div:nth-child(2) > div > div > button > span")
        if elems_1:
            elem_1 = elems_1[0]
            wait.until(EC.element_to_be_clickable(elem_1))
            elem_1.click()

def logout():
    print("LOGOUT")
    # 1. Chờ avatar load
    avatar = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#wraptLogin > div > a")
    ))

    # 2. Di chuột để mở menu
    action = ActionChains(driver)
    action.move_to_element(avatar).perform()

    # 3. Chờ menu xuất hiện và click Logout
    logout_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#wraptLogin > div > div > ul > li > a")
    ))
    logout_btn.click()


def scroll_to_y(y, step=2000):
    while True:
        current = driver.execute_script("return window.pageYOffset")
        if current + step >= y:
            driver.execute_script("window.scrollTo(0, arguments[0]);", y)
            break

        driver.execute_script("window.scrollBy(0, arguments[0]);", step)
        time.sleep(0.3)


def vote():
    # wait.until(
    #     lambda d: d.execute_script("""
    #         return performance.getEntriesByType('resource')
    #             .filter(r => r.initiatorType === 'xmlhttprequest' || r.initiatorType === 'fetch')
    #             .every(r => r.responseEnd > 0);
    #     """)
    # )
    print("VOTE")
    elem = driver.find_element(By.CSS_SELECTOR, "#root-wrapt > div.weyoung-body > div.main-content > div.wy-category.idol14 > div:nth-child(4) > div.cate-nominees > ul > li:nth-child(3)")
    if "Cường Bạch" in elem.text:
        CATEGORIES = [
            # (2, 1),
            # (3, 1),
            (4, 3),
            # (5, 1),
        ]
    else:
        CATEGORIES = [
            # (2, 1),
            # (3, 1),
            (4, 4),
            # (5, 1),
        ]
    for tab_idx, nominee_idx in CATEGORIES:
        # CSS nominee info
        info_css = (
            "#root-wrapt > div.weyoung-body > div.main-content > "
            f"div.wy-category.idol14 > div:nth-child({tab_idx}) > "
            f"div.cate-nominees > ul > li:nth-child({nominee_idx}) > "
            "div.nominee-info"
        )
        if tab_idx == 2:
            scroll_to_y(5000.015625)
        if tab_idx == 3:
            scroll_to_y(7828.859375)
        if tab_idx == 4:
            scroll_to_y(10000)
        if tab_idx == 5:
            scroll_to_y(11546.703125)
        time.sleep(1)
        vote_css = info_css.replace(
            "div.nominee-info",
            "div.nominee-vote.js-vote-item > div > a"
        )
        voted_css = (
            "#root-wrapt > div.weyoung-body > div.main-content > "
            f"div.wy-category.idol14 > div:nth-child({tab_idx}) > "
            f"div.cate-nominees > ul > li:nth-child({nominee_idx}) > div.nominee-vote.js-vote-item.voted > div > a"
        )

        voted_btns = driver.find_elements(By.CSS_SELECTOR, voted_css)
        if voted_btns:
            print("⏭ Không có nút vote, skip")
            continue

        vote_btns = driver.find_elements(By.CSS_SELECTOR, vote_css)
        if not vote_btns:
            continue
        vote_btn = vote_btns[0]
        wait.until(EC.element_to_be_clickable(vote_btn))
        vote_btn.click()
        while True:
            if driver.find_elements(By.CSS_SELECTOR, voted_css):
                print("✅ Đã vote")
                break
            vote_btn.click()
            time.sleep(10)

def reset_is_done(csv_path: str):
    df = pd.read_csv(csv_path)

    if "is_done" not in df.columns:
        raise ValueError("Column 'is_done' not found")

    df["is_done"] = df["is_done"].replace(1, 0)

    df.to_csv(csv_path, index=False)

def main(file):
    df = pd.read_csv(file)

    for i in range(len(df)):
        print("========================")
        print(f"TÀI KHOẢN {i}")
        print("========================")
        if df.loc[i, "is_done"] == 0:
            if preload():
                time.sleep(2)
                login(df.loc[i, "Mail"], df.loc[i, "Pass"])
                time.sleep(3)
                checkpoint_1 = driver.find_elements(By.ID, "wraptNotLogin")
                if checkpoint_1 and checkpoint_1[0].is_displayed():
                    driver.execute_cdp_cmd("Network.clearBrowserCache", {})
                    driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
                    df.loc[i, "is_done"] = 2
                    df.to_csv(file, index=False)
                    continue
                checkpoint_2 = driver.find_elements(
                    By.CSS_SELECTOR, "#next > div > div > a")
                if checkpoint_2 and checkpoint_2[0].is_displayed():
                    driver.execute_cdp_cmd("Network.clearBrowserCache", {})
                    driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
                    df.loc[i, "is_done"] = 2
                    df.to_csv(file, index=False)
                    continue

                vote()
                driver.execute_cdp_cmd("Network.clearBrowserCache", {})
                driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
                df.loc[i, "is_done"] = 1
                df.to_csv(file, index=False)
            else:
                driver.execute_cdp_cmd("Network.clearBrowserCache", {})
                driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
                df.loc[i, "is_done"] = 2
                df.to_csv(file, index=False)

    reset_is_done(str(args.file + ".csv"))


if __name__ == "__main__":
    main(str(args.file + ".csv"))