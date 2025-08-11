import base64
import hashlib
import json
import os
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timedelta

from cryptography.fernet import Fernet

# Windows 註冊表支援
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

class HardwareInfo:
    """專門負責獲取硬體ID和系統資訊的類別，不依賴金鑰。"""

    def run_powershell_command(self, command, timeout=10):
        try:
            full_command = ["powershell", "-Command", command]
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
                encoding='utf-8',
                errors='ignore'
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def get_system_hardware_info(self):
        system_info = {}
        try:
            if platform.system() == "Windows":
                # 使用 wmic 獲取主板、BIOS 和 CPU 資訊
                bios_info = self.run_powershell_command("Get-CimInstance Win32_BIOS | Select-Object SerialNumber, SMBIOSBIOSVersion | Format-List")
                board_info = self.run_powershell_command("Get-CimInstance Win32_BaseBoard | Select-Object SerialNumber | Format-List")
                
                system_info['os_name'] = self.run_powershell_command("Get-CimInstance Win32_OperatingSystem | Select-Object Caption | Format-List")
                system_info['windows_version'] = self.run_powershell_command("Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion' -Name DisplayVersion | Select-Object -ExpandProperty DisplayVersion")
                system_info['windows_build'] = self.run_powershell_command("Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion' -Name CurrentBuildNumber | Select-Object -ExpandProperty CurrentBuildNumber")
                system_info['windows_edition'] = self.run_powershell_command("Get-CimInstance Win32_OperatingSystem | Select-Object OSArchitecture | Format-List")
                system_info['manufacturer'] = self.run_powershell_command("Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer | Format-List")

                cpu_info = self.run_powershell_command("Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | Format-List")
                
                system_info['serial_number_bios'] = bios_info.split('\n')[0].replace("SerialNumber : ", "").strip() if bios_info else ""
                system_info['smbios_version'] = bios_info.split('\n')[1].replace("SMBIOSBIOSVersion : ", "").strip() if bios_info and len(bios_info.split('\n')) > 1 else ""
                system_info['serial_number_board'] = board_info.split('\n')[0].replace("SerialNumber : ", "").strip() if board_info else ""
                
                cpu_details = {}
                if cpu_info:
                    for line in cpu_info.split('\n'):
                        if ":" in line:
                            key, value = line.split(':', 1)
                            cpu_details[key.strip()] = value.strip()
                system_info['cpu_name'] = cpu_details.get('Name', 'unknown')
                system_info['cpu_cores'] = cpu_details.get('NumberOfCores', 'unknown')
                system_info['cpu_threads'] = cpu_details.get('NumberOfLogicalProcessors', 'unknown')
                
                mem_info = self.run_powershell_command("Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory | Format-List")
                system_info['total_memory'] = mem_info.replace("TotalPhysicalMemory : ", "").strip() if mem_info else "unknown"

        except Exception as e:
            system_info['error'] = str(e)
            
        system_info['platform_detailed'] = platform.platform(terse=False)
        system_info['machine'] = platform.machine()
        system_info['processor'] = platform.processor()
        system_info['system'] = platform.system()
        
        return system_info

    def get_hardware_id(self):
        try:
            combined_string = ""
            if platform.system() == "Windows":
                # Get BIOS Serial Number
                bios_serial = self.run_powershell_command("wmic bios get serialnumber")
                if bios_serial:
                    combined_string += bios_serial.split('\n')[2].strip()
                
                # Get Motherboard Serial Number
                board_serial = self.run_powershell_command("wmic baseboard get serialnumber")
                if board_serial:
                    combined_string += board_serial.split('\n')[2].strip()
                
                # Get CPU ID
                cpu_id = self.run_powershell_command("wmic cpu get processorid")
                if cpu_id:
                    combined_string += cpu_id.split('\n')[2].strip()
                
                # Get Windows Product Key (使用 Regedit 獲取，更穩定)
                if WINREG_AVAILABLE:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                        product_id, _ = winreg.QueryValueEx(key, "ProductId")
                        combined_string += product_id
                    except FileNotFoundError:
                        pass
                
            else: # For non-Windows systems (e.g., Linux/macOS)
                combined_string += str(uuid.getnode())

            # Fallback if the combined string is empty
            if not combined_string:
                combined_string = str(uuid.uuid4())
            
            # Hash the combined string to generate a unique ID
            hardware_id = hashlib.md5(combined_string.encode('utf-8')).hexdigest()
            print(f"Hardware ID generated: {hardware_id}")
            return hardware_id
            
        except Exception as e:
            print(f"Error getting hardware ID: {e}")
            return None

    def validate_hardware_id_format(self, hardware_id):
        return hardware_id and isinstance(hardware_id, str) and len(hardware_id) == 32 and all(c in "0123456789abcdef" for c in hardware_id)

class LicenseManager:
    """專門負責授權生成與驗證的類別，需要金鑰才能初始化。"""

    def __init__(self):
        try:
            # 從環境變數中讀取金鑰，確保後端安全
            key_from_env = os.environ.get('LICENSE_KEY')
            if not key_from_env:
                raise ValueError("Environment variable 'LICENSE_KEY' not set.")
            key_bytes = key_from_env.encode('utf-8')
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            self.fernet = Fernet(fernet_key)
            print("🔑 License generator initialized from environment variable.")
        except Exception as e:
            print(f"Error initializing LicenseManager: {e}")
            sys.exit(1)

    def generate_license_content(self, customer_name, hardware_id, expiry_days):
        try:
            expiry_date = datetime.now() + timedelta(days=expiry_days)
            license_data = {
                "customer_name": customer_name,
                "hardware_id": hardware_id,
                "expiry_date": expiry_date.isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            json_data = json.dumps(license_data, indent=4).encode('utf-8')
            encrypted_data = self.fernet.encrypt(json_data)
            
            return encrypted_data
        except Exception as e:
            print(f"Error generating license content: {e}")
            return None

    def validate_license_file(self, hardware_id, license_file_path):
        try:
            with open(license_file_path, "rb") as f:
                encrypted_data = f.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode('utf-8'))
            
            # Check hardware ID
            if license_data.get("hardware_id") != hardware_id:
                print("Hardware ID mismatch!")
                return False
            
            # Check expiry date
            expiry_date = datetime.fromisoformat(license_data.get("expiry_date"))
            if datetime.now() > expiry_date:
                print("License has expired!")
                return False
                
            return True
        except Exception as e:
            print(f"Error validating license file: {e}")
            return False
# 測試函數
# 測試函數
def test_enhanced_system_detection():
    """測試增強的系統偵測功能"""
    print("Testing System Detection...")
    print("="*50)
    
    try:
        # 使用正確的類別名稱
        hardware_info = HardwareInfo()
        
        print("\n1. 測試硬體ID生成...")
        hardware_id = hardware_info.get_hardware_id()
        if hardware_id:
            print(f"Hardware ID: {hardware_id}")
            print(f"格式驗證: {'有效' if hardware_info.validate_hardware_id_format(hardware_id) else '❌ 無效'}")
            print(f"ID長度: {len(hardware_id)} 字符")
        else:
            print("無法生成硬體ID")
        
        print("\n2. 測試系統硬體資訊獲取...")
        system_hardware_info = hardware_info.get_system_hardware_info()
        if system_hardware_info:
            print("系統硬體資訊:")
            for key, value in system_hardware_info.items():
                if value and value != "unknown" and value != "":
                    # 清理格式化的數據
                    if isinstance(value, str):
                        # 移除多餘的空白和格式字符
                        cleaned_value = value.replace('\n', ' ').replace('\r', '').strip()
                        if cleaned_value:
                            print(f"   {key}: {cleaned_value}")
                    else:
                        print(f"   {key}: {value}")
        else:
            print("無法獲取系統硬體資訊")
        
        print("\n3. 測試基本系統資訊...")
        print("基本系統資訊:")
        print(f"   平台: {platform.platform()}")
        print(f"   系統: {platform.system()}")
        print(f"   機器類型: {platform.machine()}")
        print(f"   處理器: {platform.processor()}")
        print(f"   Python版本: {platform.python_version()}")
        
        # 只有在設置了環境變數的情況下才測試 LicenseManager
        print("\n4. 測試許可證管理器...")
        license_key = os.environ.get('LICENSE_KEY')
        if license_key:
            try:
                license_manager = LicenseManager()
                print("LicenseManager 初始化成功")
                
                # 測試許可證生成
                if hardware_id:
                    print("\n5. 測試許可證生成...")
                    license_content = license_manager.generate_license_content(
                        "Test User", hardware_id, 30
                    )
                    if license_content:
                        print("許可證生成成功")
                        print(f"許可證大小: {len(license_content)} 字節")
                        
                        # 測試保存和驗證許可證
                        test_license_file = "test_license.lic"
                        try:
                            with open(test_license_file, "wb") as f:
                                f.write(license_content)
                            print(f"許可證文件已保存: {test_license_file}")
                            
                            # 驗證許可證
                            is_valid = license_manager.validate_license_file(hardware_id, test_license_file)
                            print(f"許可證驗證: {'有效' if is_valid else '無效'}")
                            
                            # 清理測試文件
                            os.remove(test_license_file)
                            print("測試文件已清理")
                            
                        except Exception as e:
                            print(f"許可證文件操作失敗: {e}")
                    else:
                        print("許可證生成失敗")
                else:
                    print("跳過許可證生成測試（無硬體ID）")
                    
            except Exception as e:
                print(f"LicenseManager 初始化失敗: {e}")
        else:
            print("跳過 LicenseManager 測試（未設置 LICENSE_KEY 環境變數）")
            print("要測試許可證功能，請設置環境變數:")
            print("export LICENSE_KEY='YourSecretKey32CharsLongString'")
        
        print("\n" + "="*50)
        print("系統偵測測試完成")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        print(f"錯誤類型: {type(e).__name__}")
        return False
    
    return True


def test_hardware_id_consistency():
    """測試硬體ID的一致性"""
    print("\n" + "="*50)
    print("測試硬體ID一致性...")
    
    try:
        hardware_info = HardwareInfo()
        
        # 生成多次硬體ID，確保一致性
        ids = []
        for i in range(3):
            hardware_id = hardware_info.get_hardware_id()
            if hardware_id:
                ids.append(hardware_id)
                print(f"第 {i+1} 次生成: {hardware_id}")
            else:
                print(f"第 {i+1} 次生成失敗")
        
        if len(set(ids)) == 1 and len(ids) > 0:
            print("硬體ID生成一致")
        elif len(ids) > 0:
            print("硬體ID生成不一致")
        else:
            print("無法生成硬體ID")
            
    except Exception as e:
        print(f"一致性測試失敗: {e}")


def main_test():
    """主測試函數"""
    print("=== QCIAutomate License Generator 測試 ===")
    print("="*50)
    
    # 執行主要測試
    test_result = test_enhanced_system_detection()
    
    # 執行一致性測試
    test_hardware_id_consistency()
    
    print("\n" + "="*50)
    if test_result:
        print("所有測試完成")
    else:
        print("測試過程中發現問題")
    
    return test_result


if __name__ == '__main__':
    main_test()