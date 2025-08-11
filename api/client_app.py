import requests
import json
import os
import sys

from license_generator_web import HardwareInfo


from license_generator_web import HardwareInfo, LicenseManager

VERCEL_API_URL = "https://qciautomate-license-github-io.vercel.app/api/generate-for-app" 

def get_local_hardware_id():
    """獲取本機硬件ID"""
    try:
        # 創建許可證生成器實例
        hardware_info = HardwareInfo()
        hardware_id = hardware_info.get_hardware_id()
        return hardware_id
    except Exception as e:
        print(f"獲取本機硬件ID時發生錯誤: {e}")
        return None
def send_request_to_server(hardware_id, customer_name="My Client App", expiry_days=365):
    """向服務器發送請求生成許可證"""
    try:
        payload = {
            "hardware_id": hardware_id,
            "customer_name": customer_name,
            "expiry_days": expiry_days
        }
        print("正在向服務器請求生成許可證...")
        print(f"請求數據: {json.dumps(payload, indent=2)}")
        # 設置超時和重試
        response = requests.post(
            VERCEL_API_URL, 
            json=payload, 
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        return response
    except requests.exceptions.Timeout:
        print("請求超時，請檢查網絡連接")
        return None
    except requests.exceptions.ConnectionError:
        print("連接錯誤，請檢查網絡連接或服務器狀態")
        return None
    except requests.exceptions.RequestException as e:
        print(f"網絡請求錯誤：{e}")
        return None        

def save_license_file(content, filename="license.lic"):
    """保存許可證文件"""
    try:
        with open(filename, "wb") as f:
            f.write(content)
        
        file_path = os.path.abspath(filename)
        file_size = os.path.getsize(filename)
        
        print(f"成功！許可證文件已保存")
        print(f"文件路徑: {file_path}")
        print(f"文件大小: {file_size} 字節")
        
        return True
    except Exception as e:
        print(f"保存文件時發生錯誤: {e}")
        return False
def main():
    print("=" * 60)
    print("QCIAutomate 許可證客戶端應用程式")
    print("=" * 60)
    
    try:
        # 步驟 1: 獲取本機硬件ID
        print("\n步驟 1: 獲取本機硬件ID...")
        hardware_id = get_local_hardware_id()
        
        if not hardware_id:
            print("錯誤：無法獲取本機硬件ID")
            input("\n按 Enter 鍵退出...")
            return

        print(f"成功獲取本機硬件ID: {hardware_id}")
        print(f"硬件ID (前8位): {hardware_id[:8]}...")
        
        # 步驟 2: 向服務器請求生成許可證
        print("\n步驟 2: 向服務器請求生成許可證...")
        response = send_request_to_server(hardware_id)
        
        if response is None:
            print("無法連接到服務器")
            input("\n按 Enter 鍵退出...")
            return
        
        # 步驟 3: 處理服務器響應
        print(f"\n步驟 3: 處理服務器響應...")
        print(f"   HTTP 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            # 成功，保存許可證文件
            if save_license_file(response.content):
                print("\n許可證生成完成！")
                print("   您現在可以使用生成的 license.lic 文件")
            else:
                print("\n許可證生成失敗：無法保存文件")
        else:
            # 失敗，顯示錯誤信息
            try:
                error_data = response.json()
                error_message = error_data.get('error', '未知錯誤')
                print(f"服務器錯誤 ({response.status_code}): {error_message}")
            except json.JSONDecodeError:
                print(f"服務器錯誤 ({response.status_code}): 無法解析服務器響應")
                print(f"響應內容: {response.text[:200]}...")

    except KeyboardInterrupt:
        print("\n\n用戶中斷操作")
    except Exception as e:
        print(f"\n發生未知錯誤：{e}")
        print(f"錯誤類型: {type(e).__name__}")

    # 保持窗口開啟
    print("\n" + "=" * 60)
    input("按 Enter 鍵退出...")
if __name__ == "__main__":
    main()