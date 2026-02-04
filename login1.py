import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import shutil
import argparse
from pathlib import Path

# CẤU HÌNH
EXCEL_FILE = "account1.csv"
WECHOICE_URL = "https://wechoice.vn/"
BASE_DIR = str(Path.cwd())

parser = argparse.ArgumentParser(description="Vote automation")
parser.add_argument("--file", type=str, default="account1", help="Đường dẫn file account CSV")
args = parser.parse_args()

user_data_path = os.path.join(BASE_DIR, args.file)
if os.path.exists(user_data_path):
    try:
        shutil.rmtree(user_data_path)
    except PermissionError:
        print(f"⚠ Không thể xóa thư mục cũ. Đang sử dụng dữ liệu hiện tại...")

class WeChoiceBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.main_handle = None
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
    
    def clear_browser_data(self):
        """Reset sạch trình duyệt bằng lệnh CDP"""
        print("    → [CDP] Đang xóa toàn bộ Cache và Cookies...")
        try:
            self.driver.execute_cdp_cmd("Network.clearBrowserCache", {})
            self.driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            print("      ✓ Trình duyệt đã được đưa về trạng thái sạch.")
        except Exception as e:
            print(f"      ⚠ Lỗi CDP: {e}")
    
    def login(self, email, password):
        """Bước 1: Đăng nhập vào WeChoice qua Google"""
        print(f"\n{'='*60}")
        print(f"BƯỚC 1: ĐĂNG NHẬP")
        print(f"{'='*60}")
        print(f"    → Email: {email}")
        
        try:
            # Mở trang chủ WeChoice
            self.driver.get(WECHOICE_URL)
            self.main_handle = self.driver.current_window_handle
            
            # Click nút đăng nhập
            login_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.login-btn")))
            self.driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)
            
            # Vào iframe nút Google
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                if "gsi/button" in (iframe.get_attribute("src") or ""):
                    self.driver.switch_to.frame(iframe)
                    break
            
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button']"))).click()
            self.driver.switch_to.default_content()
            time.sleep(1.5)
            
            # Chuyển sang popup Google Login
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Nhập email
            print("    → Đang nhập email...")
            email_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            email_input.send_keys(email)
            email_input.send_keys(Keys.ENTER)
            time.sleep(3)
            
            # Nhập password
            print("    → Đang nhập password...")
            pass_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            pass_input.send_keys(password)
            pass_input.send_keys(Keys.ENTER)
            time.sleep(3)
            
            # Xử lý checkpoints
            self.handle_all_checkpoints()
            
            # Quay về trang chủ WeChoice
            print("    → Đang quay về trang chủ WeChoice...")
            try:
                WebDriverWait(self.driver, 15).until(lambda d: len(d.window_handles) == 1)
                self.driver.switch_to.window(self.main_handle)
            except:
                if len(self.driver.window_handles) > 0:
                    self.driver.switch_to.window(self.driver.window_handles[0])
            
            time.sleep(2)
            
            # Kiểm tra đăng nhập thành công
            if "wechoice.vn" not in self.driver.current_url:
                print("      ✗ ĐĂNG NHẬP THẤT BẠI!")
                return False
            
            print("      ✓ ĐĂNG NHẬP THÀNH CÔNG!")
            return True
            
        except Exception as e:
            print(f"      ✗ Lỗi đăng nhập: {e}")
            return False
    
    def handle_all_checkpoints(self):
        """Xử lý tất cả các checkpoint của Google"""
        print("    → Đang xử lý checkpoints...")

        elems = self.driver.find_elements(By.ID, "confirm")
        if elems:
            elem = elems[0]
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem))
            elem.click()
            time.sleep(1.5)
            elems_1 = self.driver.find_elements(
                By.CSS_SELECTOR, "#yDmH0d > c-wiz > main > div.JYXaTc.F8PBrb > div > div > div:nth-child(2) > div > div > button > span")
            if elems_1:
                elem_1 = elems_1[0]
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem_1))
                elem_1.click()
        elems = self.driver.find_elements(By.CSS_SELECTOR, "#gaplustosNext > div > button > span")
        if elems:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elem = elems[0]
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem))
            elem.click()
            time.sleep(1.5)
            elems_1 = self.driver.find_elements(
                By.CSS_SELECTOR, "#yDmH0d > c-wiz > main > div.JYXaTc.F8PBrb > div > div > div:nth-child(2) > div > div > button > span")
            if elems_1:
                elem_1 = elems_1[0]
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem_1))
                elem_1.click()
        # for _ in range(5):
        #     curr_url = self.driver.current_url
        #     elems = self.driver.find_elements(By.CSS_SELECTOR, "#gaplustosNext > div > button > span")
        #     try:
        #         # CASE A: Checkpoint Điều khoản
        #         print("      [!] Phát hiện Checkpoint Điều khoản. Click 'Tôi hiểu'...")
        #         if "speedbump" in curr_url or "gaplustos" in curr_url:
        #             self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #             time.sleep(2)
        #             btns = self.driver.find_elements(By.TAG_NAME, "button")
        #             for b in btns:
        #                 if any(x in b.text.lower() for x in ["hiểu", "tôi hiểu"]):
        #                     self.driver.execute_script("arguments[0].click();", b)
        #                     time.sleep(3)
        #                     continue

        #         # CASE B: Chỉ chạy nếu CASE A KHÔNG TRIGGER
        #         if elems:
        #             self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #             elem = elems[0]
        #             WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem))
        #             elem.click()
        #             time.sleep(3)
        #             elems_1 = self.driver.find_elements(
        #                 By.CSS_SELECTOR,
        #                 "#yDmH0d > c-wiz > main > div.JYXaTc.F8PBrb > div > div > "
        #                 "div:nth-child(2) > div > div > button > span"
        #             )
        #             if elems_1:
        #                 elem_1 = elems_1[0]
        #                 WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem_1))
        #                 elem_1.click()
        #                 continue

        #         # # Checkpoint 1: Workspace Terms / Speedbump (Tôi hiểu)
        #         # if "speedbump" in curr_url or "gaplustos" in curr_url:
        #         #     print("      [!] Phát hiện Checkpoint Điều khoản. Click 'Tôi hiểu'...")
        #         #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #         #     time.sleep(2)
        #         #     btns = self.driver.find_elements(By.TAG_NAME, "button")
        #         #     for b in btns:
        #         #         if any(x in b.text.lower() for x in ["hiểu", "#confirm", "understand", "agree", "đồng ý"]):
        #         #             self.driver.execute_script("arguments[0].click();", b)
        #         #             time.sleep(3)
        #         #             break
                
        #         # elif elems:
        #         #     scroll_to_y(3000)
        #         #     elem = elems[0]
        #         #     WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem))
        #         #     elem.click()
        #         #     time.sleep(3)
        #         #     elems_1 = self.driver.find_elements(
        #         #         By.CSS_SELECTOR, "#rrJN5c > c-wiz > main > div.aJAbCd.zbvklb > div > div > div:nth-child(2) > div > div > button > span")
        #         #     if elems_1:
        #         #         elem_1 = elems_1[0]
        #         #         WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable(elem_1))
        #         #         elem_1.click()
        #         #         break
                
        #         # Checkpoint 2: OAuth Consent (Continue)
        #         if "oauth" in curr_url or "consent" in curr_url:
        #             print("      [!] Phát hiện Checkpoint Xác nhận. Click 'Continue'...")
        #             btns = self.driver.find_elements(By.TAG_NAME, "button")
        #             for b in btns:
        #                 if any(x in b.text.lower() for x in ["continue", "tiếp tục"]):
        #                     self.driver.execute_script("arguments[0].click();", b)
        #                     time.sleep(3)
        #                     continue
        #         else: break
        #     except: break
        #     time.sleep(2)
            
            # Checkpoint 1: Confirm button
            # elems = self.driver.find_elements(By.ID, "confirm")
            # if elems:
            #     print("      [!] Checkpoint 1: Confirm")
            #     elem = elems[0]
            #     WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(elem))
            #     self.driver.execute_script("arguments[0].click();", elem)
            #     time.sleep(5)
                
            #     # Sub-button
            #     elems_1 = self.driver.find_elements(
            #         By.CSS_SELECTOR, "#yDmH0d > c-wiz > main > div.JYXaTc.F8PBrb > div > div > div:nth-child(2) > div > div > button")
            #     if elems_1:
            #         self.driver.execute_script("arguments[0].click();", elems_1[0])
            #         time.sleep(5)
            
            # Checkpoint 2: Terms of Service
            # elems = self.driver.find_elements(By.CSS_SELECTOR, "#gaplustosNext > div > button > span")
            # if elems:
            #     print("      [!] Checkpoint 2: Terms of Service")
            #     self.scroll_to_y(3000)
            #     time.sleep(2)
            #     elem = elems[0]
            #     WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(elem))
            #     self.driver.execute_script("arguments[0].click();", elem)
            #     time.sleep(5)
                
            #     # Checkpoint 3: Continue
            #     print("      [!] Phát hiện Checkpoint Xác nhận. Click 'Continue'...")
            #     btns = self.driver.find_elements(By.TAG_NAME, "button")
            #     for b in btns:
            #         if any(x in b.text.lower() for x in ["continue", "tiếp tục"]):
            #             self.driver.execute_script("arguments[0].click();", b)
            #             time.sleep(5)
            #             break
            
            print("      ✓ Đã xử lý hết checkpoints")
            
        # except Exception as e:
        #     print(f"      ⚠ Lỗi checkpoint: {e}")

    def return_to_main(self):
        """Bước 2: Quay về trang chủ"""
        print(f"\n{'='*60}")
        print(f"BƯỚC 2: QUAY VỀ TRANG CHỦ")
        print(f"{'='*60}")
        
        try:
            self.driver.get(WECHOICE_URL)
            time.sleep(1.5)
            
            # Kiểm tra có đang ở trang chủ không
            if "wechoice.vn" in self.driver.current_url:
                print("      ✓ Đã về trang chủ WeChoice")
                return True
            else:
                print("      ✗ Không thể về trang chủ")
                return False
                
        except Exception as e:
            print(f"      ✗ Lỗi: {e}")
            return False
    
    def logout(self):
        """Bước 3: Đăng xuất"""
        print(f"\n{'='*60}")
        print(f"BƯỚC 3: ĐĂNG XUẤT")
        print(f"{'='*60}")
        
        try:
            # Tìm avatar hoặc menu user
            print("    → Đang tìm nút đăng xuất...")
            
            # Thử nhiều selector khác nhau
            logout_selectors = [
                "a.logout-btn",
                "button[class*='logout']",
                "a[href*='logout']",
                ".user-menu .logout",
                "//a[contains(text(), 'Đăng xuất')]",
                "//a[contains(text(), 'Logout')]",
            ]
            
            logout_clicked = False
            
            for selector in logout_selectors:
                try:
                    if selector.startswith("//"):
                        elem = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elem = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elem:
                        print(f"      [!] Tìm thấy nút logout: {selector}")
                        self.driver.execute_script("arguments[0].click();", elem[0])
                        time.sleep(1.5)
                        logout_clicked = True
                        break
                except:
                    continue
            
            if not logout_clicked:
                # Fallback: Clear cookies để logout
                print("      [!] Không tìm thấy nút logout, đang xóa cookies...")
                self.clear_browser_data()
                self.driver.get(WECHOICE_URL)
                time.sleep(1.5)
            
            print("      ✓ ĐĂNG XUẤT THÀNH CÔNG!")
            return True
            
        except Exception as e:
            print(f"      ⚠ Lỗi đăng xuất: {e}")
            # Force logout bằng cách xóa cookies
            self.clear_browser_data()
            return True
    
    def run_cycle(self, email, password):
        """Chạy vòng lặp: Login > Return > Logout"""
        print(f"\n{'#'*60}")
        print(f"BẮT ĐẦU VÒNG LẶP CHO: {email}")
        print(f"{'#'*60}")
        
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
            login_success = self.login(email, password)
            if not login_success:
                print("\n    ✗ VÒNG LẶP THẤT BẠI DO LỖI ĐĂNG NHẬP")
                return False
            
            # BƯỚC 2: QUAY VỀ TRANG CHỦ
            return_success = self.return_to_main()
            if not return_success:
                print("\n    ⚠ Cảnh báo: Không thể quay về trang chủ")
            
            # Chờ một chút để xem trang chủ
            print("    → Đang ở trang chủ, chờ 5 giây...")
            time.sleep(0.5)
            return True
            
            # # BƯỚC 3: ĐĂNG XUẤT
            # logout_success = self.logout()
            
            # if logout_success:
            #     print(f"\n{'='*60}")
            #     print("✓ VÒNG LẶP HOÀN TẤT THÀNH CÔNG!")
            #     print(f"{'='*60}\n")
            #     return True
            # else:
            #     print("\n    ⚠ VÒNG LẶP HOÀN TẤT NHƯNG CÓ LỖI LOGOUT")
            #     return False
                
        except Exception as e:
            print(f"\n    ✗ LỖI VÒNG LẶP: {e}")
            self.clear_browser_data()
            return False
    
    def scroll_to_y(self, y, step=2000):
        """Scroll trang web đến vị trí y"""
        while True:
            current = self.driver.execute_script("return window.pageYOffset")
            if current + step >= y:
                self.driver.execute_script("window.scrollTo(0, arguments[0]);", y)
                break
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", step)
            time.sleep(0.15)

def main(file_path):
    if not os.path.exists(file_path):
        print(f"✗ KHÔNG TÌM THẤY FILE: {file_path}")
        return
    
    df = pd.read_csv(file_path)
    
    # Đảm bảo có cột is_done
    if 'is_done' not in df.columns:
        df['is_done'] = 0
    
    bot = WeChoiceBot()
    print(f"\n{'*'*60}")
    print(f"BẮT ĐẦU CHIẾN DỊCH: {len(df)} TÀI KHOẢN")
    print(f"{'*'*60}\n")
    
    for index, row in df.iterrows():
        if str(row['is_done']) == '1':
            print(f"[Acc {index+1}/{len(df)}] {row['mail']} - ĐÃ HOÀN THÀNH, BỎ QUA")
            continue
        
        print(f"\n{'*'*60}")
        print(f"TÀI KHOẢN {index+1}/{len(df)}")
        print(f"{'*'*60}")
        
        # Chạy vòng lặp
        success = bot.run_cycle(row['mail'], row['username'])
        
        # Cập nhật trạng thái
        df.at[index, 'is_done'] = 1 if success else 2
        
        # Lưu file
        for _ in range(5):
            try:
                df.to_csv(file_path, index=False)
                print(f"    ✓ Đã lưu trạng thái: {df.at[index, 'is_done']}")
                break
            except PermissionError:
                print("    ⚠ Vui lòng ĐÓNG FILE để lưu kết quả...")
                time.sleep(1.5)
        
        # Nghỉ giữa các account
        print(f"    → Chờ 3 giây trước khi xử lý account tiếp theo...")
        time.sleep(1.5)
    
    bot.driver.quit()
    print(f"\n{'*'*60}")
    print("✓ CHIẾN DỊCH HOÀN TẤT!")
    print(f"{'*'*60}\n")

if __name__ == "__main__":
    target_file = str(args.file + ".csv")
    main(target_file)
