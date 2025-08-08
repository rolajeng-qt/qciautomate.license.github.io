import requests
import json
import os
import sys

from license_generator_web import LicenseGeneratorLogic

VERCEL_API_URL = "https://qciautomate-license-github-io.vercel.app/api/generate-for-app" 

def main():
    try:
        # 1. 获取本机的硬件ID
        license_logic = LicenseGeneratorLogic()
        hardware_id = license_logic.get_hardware_id()
        
        if not hardware_id:
            print("错误：无法获取本机硬件ID。")
            input("按任意键退出...")
            return

        print(f"成功获取本机硬件ID：{hardware_id}")
        
        # 2. 准备发送给服务器的数据
        payload = {
            "hardware_id": hardware_id,
            "customer_name": "My Client App",
            "expiry_days": 365
        }
        
        # 3. 发送POST请求到Vercel后端
        print("正在向服务器请求生成许可证...")
        response = requests.post(VERCEL_API_URL, json=payload, timeout=30)
        
        # 4. 检查服务器响应
        if response.status_code == 200:
            # 成功，保存许可证文件
            filename = "license.lic"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"成功！许可证文件已保存至：{os.path.abspath(filename)}")
        else:
            # 失败，打印错误信息
            try:
                error_data = response.json()
                print(f"服务器错误（{response.status_code}）：{error_data.get('error', '未知错误')}")
            except json.JSONDecodeError:
                print(f"服务器错误（{response.status_code}）：无法解析服务器响应。")

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")

    # 保持窗口开启，方便使用者查看
    input("按任意键退出...")

if __name__ == "__main__":
    main()