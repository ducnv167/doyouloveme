import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os
import shutil
import argparse
from pathlib import Path

from undetected_chromedriver import options

# CẤU HÌNH
EXCEL_FILE = "account1.csv"
WECHOICE_URL = "https://wechoice.vn/chi-tiet-de-cu/rising-artist-9/cuong-bach-63.htm"
BASE_DIR = str(Path.cwd())

parser = argparse.ArgumentParser(description="Vote automation")
parser.add_argument(
    "--file",
    type=str,
    default="account1",
    help="Đường dẫn file account CSV"
)

args = parser.parse_args()
user_data_path = os.path.join(BASE_DIR, args.file)
if os.path.exists(user_data_path):
    try:
        shutil.rmtree(user_data_path)
    except PermissionError:
        print(f"      ⚠ Không thể xóa thư mục cũ do đang bị chiếm dụng. Đang sử dụng dữ liệu hiện tại...")

class WeChoiceBot:
    def __init__(self):
        self.options = None
        self.driver = None
        self.wait = None
        self.main_handle = None
        
        # Khởi tạo driver lần đầu
        self.init_driver()

    def init_driver(self):
        """Khởi tạo hoặc khởi động lại trình duyệt"""
        if self.driver:
            try: 
                self.driver.quit()
            except: 
                pass
        
        print("    → Đang khởi tạo trình duyệt mới...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f"--user-data-dir={os.path.join(BASE_DIR, args.file)}")
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 25)

    def check_and_handle_recaptcha_border(self):
        """Kiểm tra và xử lý recaptcha-checkbox-border - RELOAD nếu phát hiện"""
        try:
            # Kiểm tra xem có element "recaptcha-checkbox-border" không
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "recaptcha-checkbox-border"))
            )
            print("    [!] Phát hiện recaptcha-checkbox-border → RELOAD TRANG!")
            self.driver.refresh()
            time.sleep(2.5)
            return True  # Đã reload
        except:
            return False  # Không có recaptcha-checkbox-border

    def clear_browser_data(self):
        """Reset sạch trình duyệt bằng lệnh CDP (Cache & Cookies)"""
        print("    → [CDP] Đang xóa toàn bộ Cache và Cookies...")
        try:
            self.driver.execute_cdp_cmd("Network.clearBrowserCache", {})
            self.driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            print("      ✓ Trình duyệt đã được đưa về trạng thái sạch.")
        except Exception as e:
            print(f"      ⚠ Lỗi CDP: {e}")

    def handle_checkpoints(self):
        """Vượt qua các lớp Google (Checkpoint)"""
        print("    → Đang kiểm tra các điểm chặn Google (Checkpoint)...")
        for _ in range(5):
            curr_url = self.driver.current_url
            try:
                if "speedbump" in curr_url or "gaplustos" in curr_url:
                    print("      [!] Phát hiện Checkpoint Điều khoản. Click 'Tôi hiểu'...")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2.5)
                    btns = self.driver.find_elements(By.TAG_NAME, "button")
                    for b in btns:
                        if any(x in b.text.lower() for x in ["hiểu", "tôi hiểu", "confirm", "i understand", "understand", "agree", "đồng ý", "submit"]):
                            self.driver.execute_script("arguments[0].click();", b)
                            time.sleep(1)
                            break
                
                elif "oauth" in curr_url or "consent" in curr_url:
                    print("      [!] Phát hiện Checkpoint Xác nhận. Click 'Continue'...")
                    btns = self.driver.find_elements(By.TAG_NAME, "button")
                    for b in btns:
                        if any(x in b.text.lower() for x in ["continue", "tiếp tục"]):
                            self.driver.execute_script("arguments[0].click();", b)
                            time.sleep(1.5)
                            break
                else: break
            except: break
            time.sleep(10)
    
    def reload_and_wait(self, url=None, sleep_sec=5):
        """Reload lại trang hiện tại (hoặc URL chỉ định) rồi đợi ổn định."""
        if url:
            self.driver.get(url)
        else:
            self.driver.refresh()
        time.sleep(sleep_sec / 2)


    def run_process(self, email, password):
        """Tuần tự: Xóa data -> Login -> Vote -> Xóa data"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Kiểm tra driver
                try:
                    _ = self.driver.current_url
                except:
                    print("    ⚠ Trình duyệt đã bị đóng. Đang khởi động lại...")
                    self.init_driver()
                
                # Clear data trước khi bắt đầu
                self.clear_browser_data()
                
                # BƯỚC 1: ĐĂNG NHẬP
                print(f"    → Bắt đầu Đăng nhập (lần {attempt+1}/{max_retries}): {email}")
                self.driver.get(WECHOICE_URL)
                self.main_handle = self.driver.current_window_handle
                
                # **KIỂM TRA RECAPTCHA BORDER TRƯỚC KHI LOGIN**
                if self.check_and_handle_recaptcha_border():
                    continue  # Reload rồi thử lại
                
                login_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.login-btn")))
                self.driver.execute_script("arguments[0].click();", login_btn)
                time.sleep(2.5)

                # Vào iframe nút Google
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    if "gsi/button" in (iframe.get_attribute("src") or ""):
                        self.driver.switch_to.frame(iframe)
                        break
                self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button']"))).click()
                self.driver.switch_to.default_content()
                time.sleep(2.5)

                # Popup Google Login
                if len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                
                # Nhập Mail & Pass
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(email + Keys.ENTER)
                time.sleep(3)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).send_keys(password + Keys.ENTER)
                time.sleep(3)
                
                # ========== QUAY VỀ WECHOICE ==========
                try:
                    WebDriverWait(self.driver, 15).until(lambda d: len(d.window_handles) == 1)
                    self.driver.switch_to.window(self.main_handle)
                    print("    ✓ Đã quay về cửa sổ WeChoice")
                except:
                    if len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    else:
                        self.driver.switch_to.window(self.main_handle)
                
                time.sleep(5)
                
                # Kiểm tra đăng nhập thành công
                if "wechoice.vn" not in self.driver.current_url:
                    print("      ✗ Đăng nhập thất bại (Kẹt tại Google Checkpoint).")
                    self.clear_browser_data()
                    continue  # Thử lại lần sau

                # BƯỚC 2: VOTE
                print("    → Đang thực hiện Vote...")

                def is_voted():
                    """Ưu tiên check trạng thái đã bình chọn nếu trang có hiển thị rõ."""
                    try:
                        # Ví dụ: nút đổi text 'Đã bình chọn'
                        btn = self.driver.find_element(
                            By.XPATH,
                            "//*[contains(text(), 'Đã bình chọn') or contains(text(), 'Bạn đã bình chọn')]"
                        )
                        if btn.is_displayed():
                            return True
                    except Exception:
                        pass
                    return False

                max_loop = 5
                for step in range(1, max_loop + 1):
                    print(f"      → Vòng kiểm tra vote #{step}/{max_loop}")

                    # 1. Nếu trang có hiển thị trạng thái 'Đã bình chọn' → kết thúc
                    if is_voted():
                        print("      ✓ Phát hiện trạng thái ĐÃ BÌNH CHỌN → Kết thúc.")
                        self.clear_browser_data()
                        return 1

                    try:
                        # 2. Tìm & click nút Bình chọn
                        vote_btn = self.wait.until(EC.element_to_be_clickable(
                            (By.XPATH,
                            "//a[contains(@class,'btn-vote')]"
                            " | //button[contains(@class,'btn-vote')]"
                            " | //*[contains(text(),'Bình chọn')]")
                        ))
                        self.driver.execute_script("arguments[0].click();", vote_btn)
                        print("      ✓ Đã click nút 'Bình chọn'.")

                        self.driver.switch_to.default_content()
                        time.sleep(0.5)

                        # 3. Tìm iframe reCAPTCHA (nếu có)
                        recaptcha_iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                        target_iframe = None
                        for frame in recaptcha_iframes:
                            title = frame.get_attribute("title") or ""
                            src = frame.get_attribute("src") or ""
                            if "recaptcha" in src or "recaptcha" in title:
                                target_iframe = frame
                                break

                        if not target_iframe:
                            # 👉 CASE CỦA BẠN: ĐÃ CLICK, KHÔNG CÓ CAPTCHA → COI NHƯ THÀNH CÔNG
                            print("      ✓ Đã click, không thấy iframe reCAPTCHA → COI NHƯ ĐÃ VOTE XONG.")
                            time.sleep(1.5)
                            self.clear_browser_data()
                            return 1

                        # 4. Có captcha → xử lý theo rule của bạn
                        self.driver.switch_to.frame(target_iframe)

                        # 4a. Nếu là recaptcha-checkbox-border → RELOAD rồi quay lại vòng for (check lại từ đầu)
                        try:
                            border = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
                            )
                            if border.is_displayed():
                                print("      [!] Captcha checkbox (recaptcha-checkbox-border) → RELOAD TRANG.")
                                self.driver.switch_to.default_content()
                                self.reload_and_wait(WECHOICE_URL, sleep_sec=5)
                                continue  # quay lại vòng for → check lại bước 1
                        except Exception:
                            pass

                        # 5. Sau khi xử lý captcha, nếu trang cho hiển thị trạng thái, thử check lại:
                        if is_voted():
                            print("      ✓ Sau captcha: phát hiện ĐÃ BÌNH CHỌN → Kết thúc.")
                            self.clear_browser_data()
                            return 1

                        # Nếu không có trạng thái rõ ràng, nhưng đã qua captcha thì coi như xong:
                        print("      ✓ Qua captcha nhưng không thấy trạng thái rõ → COI NHƯ THÀNH CÔNG.")
                        self.clear_browser_data()
                        return 1

                    except Exception as e:
                        print(f"      ✗ Lỗi trong vòng vote #{step}: {e}")
                        self.driver.switch_to.default_content()
                        self.reload_and_wait(WECHOICE_URL, sleep_sec=5)

                print("      ✗ Không xác định được trạng thái đã bình chọn sau nhiều lần thử.")
                self.clear_browser_data()
                return 2

            except Exception as e:
                print(f"    ✗ Lỗi quy trình: {e}")
                self.clear_browser_data()
                return 2

def reset_is_done(csv_path: str):
    df = pd.read_csv(csv_path)
    if "is_done" not in df.columns:
        raise ValueError("Column 'is_done' not found")
    df["is_done"] = df["is_done"].replace(1, 0)
    df.to_csv(csv_path, index=False)

def main(file_path):
    if not os.path.exists(file_path):
        print(f"✗ KHÔNG TÌM THẤY FILE: {file_path}")
        return

    df = pd.read_csv(file_path)
    
    if 'is_done' not in df.columns:
        df['is_done'] = 0
        
    bot = WeChoiceBot()
    print(f"✓ Bắt đầu chu kỳ cho {len(df)} tài khoản sử dụng file: {file_path}")

    for index, row in df.iterrows():
        if str(row['is_done']) == '1': 
            continue
        
        print(f"\n[Acc {index+1}/{len(df)}] {row['mail']}")
        
        status = bot.run_process(row['mail'], row['username'])
        df.at[index, 'is_done'] = status
        
        for _ in range(5):
            try:
                df.to_csv(file_path, index=False)
                break
            except PermissionError:
                print("    ⚠ Vui lòng ĐÓNG FILE để lưu kết quả...")
                time.sleep(2)
        
        print(f"    ✓ Đã lưu trạng thái: {status}")
        time.sleep(1)

    bot.driver.quit()
    print("\n✓ CHIẾN DỊCH HOÀN TẤT.")
    reset_is_done(file_path)

if __name__ == "__main__":
    target_file = str(args.file + ".csv")
    main(target_file)
