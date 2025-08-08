import hashlib
import json
import uuid
import platform
import subprocess
import base64
import sys
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

# Windows 註冊表支援
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

class LicenseGeneratorLogic:
    """
    Enhanced license generator with robust Windows 11 detection
    that works even when wmic is not available.
    """
    def __init__(self):
        """
        Initializes the license generator with a fixed secret key.
        """
        key = b'QCIAutomate2024SecretKey32Chars!'
        fernet_key = base64.urlsafe_b64encode(key)
        self.fernet = Fernet(fernet_key)
        print("🔑 License generator initialized with fixed key")

    def run_powershell_command(self, command, timeout=10):
        """
        執行 PowerShell 命令 (用於替代 wmic)
        """
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
        except Exception as e:
            print(f"⚠️  PowerShell command failed: {e}")
            return None

    def get_windows_version_info(self):
        """
        獲取詳細的 Windows 版本資訊，使用多種方法確保相容性
        """
        version_info = {
            "os_name": "Unknown",
            "version": "Unknown",
            "build": "Unknown",
            "edition": "Unknown"
        }
        
        try:
            if platform.system() != "Windows":
                return version_info
            
            # 方法 1: 使用 Windows Registry (最可靠)
            if WINREG_AVAILABLE:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        
                        # 產品名稱
                        try:
                            product_name = winreg.QueryValueEx(key, "ProductName")[0]
                            version_info["os_name"] = product_name
                        except FileNotFoundError:
                            pass
                        
                        # 版本號
                        try:
                            display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                            version_info["version"] = display_version
                        except FileNotFoundError:
                            try:
                                release_id = winreg.QueryValueEx(key, "ReleaseId")[0]
                                version_info["version"] = release_id
                            except FileNotFoundError:
                                pass
                        
                        # Build 號
                        try:
                            build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                            version_info["build"] = build
                            
                            # 根據 Build 號判斷是否為 Windows 11
                            build_num = int(build)
                            if build_num >= 22000:
                                if "Windows 10" in version_info["os_name"]:
                                    version_info["os_name"] = version_info["os_name"].replace("Windows 10", "Windows 11")
                                elif version_info["os_name"] == "Unknown":
                                    version_info["os_name"] = "Windows 11"
                                    
                        except (FileNotFoundError, ValueError):
                            pass
                        
                        # 版本類型
                        try:
                            edition = winreg.QueryValueEx(key, "EditionID")[0]
                            version_info["edition"] = edition
                        except FileNotFoundError:
                            pass
                
                except Exception as e:
                    print(f"⚠️  Registry access failed: {e}")
            
            # 方法 2: 使用 PowerShell (替代 wmic)
            if version_info["os_name"] == "Unknown" or version_info["build"] == "Unknown":
                try:
                    ps_command = """
                    $os = Get-CimInstance -ClassName Win32_OperatingSystem
                    $cs = Get-CimInstance -ClassName Win32_ComputerSystem
                    Write-Output "$($os.Caption)|$($os.Version)|$($os.BuildNumber)|$($cs.Model)|$($cs.Manufacturer)"
                    """
                    
                    result = self.run_powershell_command(ps_command)
                    if result:
                        parts = result.split('|')
                        if len(parts) >= 3:
                            if version_info["os_name"] == "Unknown":
                                version_info["os_name"] = parts[0].strip()
                            if version_info["build"] == "Unknown":
                                version_info["build"] = parts[2].strip()
                                
                                # 再次檢查 Windows 11
                                try:
                                    build_num = int(parts[2])
                                    if build_num >= 22000 and "Windows 10" in version_info["os_name"]:
                                        version_info["os_name"] = version_info["os_name"].replace("Windows 10", "Windows 11")
                                except ValueError:
                                    pass
                    
                except Exception as e:
                    print(f"⚠️  PowerShell OS detection failed: {e}")
            
            # 方法 3: 使用 platform 模組作為備用
            if version_info["os_name"] == "Unknown":
                platform_info = platform.platform()
                if "Windows" in platform_info:
                    version_info["os_name"] = "Windows"
                    # 從 platform 資訊中提取版本
                    if "10.0.26100" in platform_info or "26100" in platform_info:
                        version_info["os_name"] = "Windows 11"
                        version_info["build"] = "26100"
                
        except Exception as e:
            print(f"❌ 獲取 Windows 版本資訊失敗: {e}")
        
        return version_info

    def get_system_hardware_info(self):
        """
        獲取硬體資訊，使用 PowerShell 替代 wmic
        """
        hardware_info = {
            "model": "unknown",
            "manufacturer": "unknown",
            "total_memory": "unknown",
            "cpu_name": "unknown",
            "cpu_cores": "unknown",
            "cpu_threads": "unknown"
        }
        
        try:
            if platform.system() != "Windows":
                return hardware_info
            
            # 使用 PowerShell 獲取系統資訊
            ps_command = """
            $cs = Get-CimInstance -ClassName Win32_ComputerSystem
            $cpu = Get-CimInstance -ClassName Win32_Processor | Select-Object -First 1
            $memory = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
            Write-Output "$($cs.Model)|$($cs.Manufacturer)|$($memory)|$($cpu.Name)|$($cpu.NumberOfCores)|$($cpu.NumberOfLogicalProcessors)"
            """
            
            result = self.run_powershell_command(ps_command)
            if result:
                parts = result.split('|')
                if len(parts) >= 6:
                    hardware_info["model"] = parts[0].strip() if parts[0].strip() else "unknown"
                    hardware_info["manufacturer"] = parts[1].strip() if parts[1].strip() else "unknown"
                    hardware_info["total_memory"] = f"{parts[2].strip()} GB" if parts[2].strip() else "unknown"
                    hardware_info["cpu_name"] = parts[3].strip() if parts[3].strip() else "unknown"
                    hardware_info["cpu_cores"] = parts[4].strip() if parts[4].strip() else "unknown"
                    hardware_info["cpu_threads"] = parts[5].strip() if parts[5].strip() else "unknown"
            
            # 如果 PowerShell 失敗，嘗試使用舊的 wmic 方法作為備用
            if hardware_info["model"] == "unknown":
                try:
                    result = subprocess.run(['wmic', 'computersystem', 'get', 'model'], 
                                          capture_output=True, text=True, timeout=5)
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        hardware_info["model"] = lines[1].strip()
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"⚠️  獲取硬體資訊失敗: {e}")
        
        return hardware_info

    def get_hardware_id(self):
        """
        生成硬體ID，增強的版本
        """
        try:
            # Get MAC address
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                             for i in range(0, 8*6, 8)][::-1])
            cpu = platform.processor()
            machine = platform.machine()
            
            # 獲取更詳細的硬體資訊
            hardware_info = self.get_system_hardware_info()
            model = hardware_info["model"]
            
            # 如果無法獲取型號，使用預設值
            if model == "unknown":
                model = "generic_pc"
            
            # Combine all collected info into a single string
            hardware_string = f"{mac}{cpu}{machine}{model}"
            
            # Use SHA256 hash to create a unique, fixed-length ID
            hardware_id = hashlib.sha256(hardware_string.encode()).hexdigest()[:32]
            print("="*50)
            print(f"Hardware ID generated: {hardware_id}")
            print(f"System Info: {platform.platform()}")
            print(f"Processor: {cpu}")
            print(f"Machine Type: {machine}")
            print(f"Model: {model}")
            print("="*50)
            return hardware_id
        except Exception as e:
            print(f"❌ Failed to get hardware ID: {e}")
            return None

    def get_system_info(self):
        """
        獲取詳細系統資訊，整合所有資訊來源
        """
        try:
            info = {
                "platform": platform.platform(),
                "system": platform.system(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
                "model": "unknown"
            }
            
            # 獲取 Windows 特有資訊
            if platform.system() == "Windows":
                # 獲取 Windows 版本資訊
                windows_info = self.get_windows_version_info()
                
                # 獲取硬體資訊
                hardware_info = self.get_system_hardware_info()
                
                # 合併資訊
                info.update({
                    "os_name": windows_info["os_name"],
                    "windows_version": windows_info["version"],
                    "windows_build": windows_info["build"],
                    "windows_edition": windows_info["edition"],
                    "model": hardware_info["model"],
                    "manufacturer": hardware_info["manufacturer"],
                    "total_memory": hardware_info["total_memory"],
                    "cpu_name": hardware_info["cpu_name"],
                    "cpu_cores": hardware_info["cpu_cores"],
                    "cpu_threads": hardware_info["cpu_threads"]
                })
                
                # 建立更好的平台描述
                if windows_info["os_name"] != "Unknown":
                    platform_parts = [windows_info["os_name"]]
                    if windows_info["version"] != "Unknown":
                        platform_parts.append(f"Version {windows_info['version']}")
                    if windows_info["build"] != "Unknown":
                        platform_parts.append(f"Build {windows_info['build']}")
                    if windows_info["edition"] != "Unknown":
                        platform_parts.append(windows_info["edition"])
                    
                    info["platform_detailed"] = " - ".join(platform_parts)
            
            return info
        except Exception as e:
            print(f"❌ Failed to get system info: {e}")
            return {"error": str(e)}

    def generate_license_content(self, username, hardware_id, expiry_days):
        """
        生成加密的授權內容
        """
        try:
            if not username or not username.strip():
                username = "Unknown User"
            
            if not hardware_id or len(hardware_id) < 8:
                raise ValueError("Invalid hardware ID")
            
            if expiry_days < 1 or expiry_days > 3650:
                raise ValueError("Expiry days must be between 1 and 3650")
            
            license_data = {
                "username": username.strip(),
                "hardware_id": hardware_id,
                "issued_date": datetime.now().isoformat(),
                "expiry_date": (datetime.now() + timedelta(days=expiry_days)).isoformat(),
                "features": ["full_access"],
                "version": "1.0.6",
                "issued_by": "QCIAutomate License Server",
                "license_type": "hardware_bound"
            }
            
            encrypted_data = self.fernet.encrypt(json.dumps(license_data).encode())
            
            print(f"License generated for: {username}")
            print(f"Hardware ID: {hardware_id[:8]}...")
            print(f"Valid for: {expiry_days} days")
            print(f"Expires: {license_data['expiry_date'][:10]}")
            
            return encrypted_data
        except Exception as e:
            print(f"❌ Failed to generate license content: {e}")
            return None

    def create_default_license_for_current_machine(self):
        """為當前機器建立預設授權檔案"""
        try:
            hardware_id = self.get_hardware_id()
            if not hardware_id:
                print("❌ Cannot create default license: Unable to get hardware ID")
                return None
            
            license_content = self.generate_license_content("Local User", hardware_id, 365)
            
            if license_content:
                print("🎉 Default license created successfully for current machine!")
                return license_content
            else:
                print("❌ Failed to create default license content")
                return None
                
        except Exception as e:
            print(f"❌ Failed to create default license: {e}")
            return None

    def validate_hardware_id(self, hardware_id):
        """驗證硬體ID格式"""
        try:
            if not hardware_id or not isinstance(hardware_id, str):
                return False
                
            if len(hardware_id) < 16 or len(hardware_id) > 64:
                return False
                
            hex_chars = set('0123456789abcdefABCDEF')
            valid_chars = sum(1 for c in hardware_id if c in hex_chars)
            
            if valid_chars / len(hardware_id) < 0.8:
                return False
                
            return True
        except Exception:
            return False

# 測試函數
def test_enhanced_system_detection():
    """測試增強的系統偵測功能"""
    print("Testing System Detection...")
    
    generator = LicenseGeneratorLogic()
    
    print("\n1. 測試 Windows 版本偵測...")
    if platform.system() == "Windows":
        windows_info = generator.get_windows_version_info()
        print("Windows 版本資訊:")
        for key, value in windows_info.items():
            print(f"   {key}: {value}")
    
    print("\n2. 測試硬體資訊獲取...")
    if platform.system() == "Windows":
        hardware_info = generator.get_system_hardware_info()
        print("硬體資訊:")
        for key, value in hardware_info.items():
            print(f"   {key}: {value}")
    
    print("\n3. 測試完整系統資訊...")
    system_info = generator.get_system_info()
    print("完整系統資訊:")
    for key, value in system_info.items():
        if value and value != "unknown":
            print(f"   {key}: {value}")
    
    print("\n4. 測試硬體ID生成...")
    hardware_id = generator.get_hardware_id()
    if hardware_id:
        print(f"Hardware ID: {hardware_id}")
        print(f"格式驗證: {'✅ 有效' if generator.validate_hardware_id(hardware_id) else '❌ 無效'}")
    
    return True

if __name__ == '__main__':
    print("=== QCIAutomate License Generator ===")
    print("="*50)
    
    test_enhanced_system_detection()