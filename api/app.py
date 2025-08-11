from flask import Flask, request, send_file, jsonify, render_template_string
from license_generator_web import HardwareInfo, LicenseManager
import os
import io
import json
import platform

app = Flask(__name__)
license_logic = LicenseManager()

@app.route('/api/generate-for-app', methods=['POST'])
def generate_for_app():
    """接收硬件ID，生成许可证文件并返回"""
    try:
        data = request.get_json()
        hardware_id = data.get('hardware_id')
        customer_name = data.get('customer_name', 'Client App User')
        expiry_days = data.get('expiry_days', 365)
        
        if not hardware_id:
            return jsonify({"error": "缺少硬件ID"}), 400

        if expiry_days < 1 or expiry_days > 3650:
            return jsonify({"error": "许可证有效期必须介于 1-3650 天之间"}), 400

        print(f"为本機应用程式生成许可证 - 用户: {customer_name}, 硬件ID: {hardware_id[:8]}..., 天数: {expiry_days}")
        
        license_content = license_logic.generate_license_content(customer_name, hardware_id, expiry_days)
        if not license_content:
            return jsonify({"error": "生成许可证内容失败"}), 500

        # 直接返回许可证文件内容，无需send_file
        return license_content, 200, {'Content-Type': 'application/octet-stream', 'Content-Disposition': 'attachment; filename=license.lic'}

    except Exception as e:
        print(f"API错误 - generate_for_app: {e}")
        return jsonify({"error": f"生成许可证文件失败: {str(e)}"}), 500
        
@app.route('/api/get-hardware-id', methods=['GET'])
def get_hardware_id():
    """API: 获取本机硬件ID（增强版 - 正确识别 Windows 11）"""
    try:
        hardware_id = license_logic.get_hardware_id()
        if not hardware_id:
            return jsonify({"error": "无法获取硬件ID"}), 500
        
        # 获取详细系统信息
        system_info = license_logic.get_system_info()
        system_info["hardware_id"] = hardware_id
        
        # 如果有详细的平台信息，使用它
        if "platform_detailed" in system_info:
            system_info["system_info"] = system_info["platform_detailed"]
        elif "system_info" not in system_info:
            system_info["system_info"] = platform.platform()
        
        # 确保返回的数据结构符合前端期望
        response_data = {
            "hardware_id": hardware_id,
            "system_info": system_info.get("system_info", platform.platform()),
            "processor": system_info.get("processor", platform.processor()),
            "machine": system_info.get("machine", platform.machine()),
            "model": system_info.get("model", "unknown")
        }
        
        # 添加额外的 Windows 信息
        if platform.system() == "Windows" and "os_name" in system_info:
            response_data.update({
                "os_name": system_info.get("os_name"),
                "windows_version": system_info.get("windows_version"),
                "windows_build": system_info.get("windows_build"),
                "windows_edition": system_info.get("windows_edition"),
                "manufacturer": system_info.get("manufacturer"),
                "cpu_name": system_info.get("cpu_name"),
                "cpu_cores": system_info.get("cpu_cores"),
                "cpu_threads": system_info.get("cpu_threads"),
                "total_memory": system_info.get("total_memory")
            })
        
        print(f"硬件ID API调用成功 - ID: {hardware_id[:8]}...")
        if "os_name" in system_info:
            print(f"检测到操作系统: {system_info['os_name']}")
        
        return jsonify(response_data)
    except Exception as e:
        print(f"API错误 - get_hardware_id: {e}")
        return jsonify({"error": f"获取硬件ID失败: {str(e)}"}), 500

@app.route('/generate', methods=['POST'])
def generate():
    """处理表单提交，生成许可证文件"""
    try:
        # 支持表单数据和JSON数据
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            customer_name = data.get('customer_name', 'Web User')
            hardware_id = data.get('hardware_id')
            expiry_days = data.get('expiry_days', 365)
        else:
            customer_name = request.form.get('customer_name', 'Web User')
            hardware_id = request.form.get('hardware_id')
            expiry_days = int(request.form.get('expiry_days', 365))

        if not hardware_id:
            return jsonify({"error": "缺少硬件ID"}), 400

        if not customer_name.strip():
            customer_name = "Web User"

        # 验证许可证有效期
        if expiry_days < 1 or expiry_days > 3650:
            return jsonify({"error": "许可证有效期必须介于 1-3650 天之间"}), 400

        print(f"生成许可证 - 用户: {customer_name}, 硬件ID: {hardware_id[:8]}..., 天数: {expiry_days}")
        
        license_content = license_logic.generate_license_content(customer_name, hardware_id, expiry_days)
        if not license_content:
            return jsonify({"error": "生成许可证内容失败"}), 500

        # 将许可证内容以文件形式返回给用户下载
        return send_file(
            io.BytesIO(license_content),
            as_attachment=True,
            download_name='license.lic',
            mimetype='application/octet-stream'
        )
    except ValueError as e:
        print(f"参数错误 - generate: {e}")
        return jsonify({"error": f"参数错误: {str(e)}"}), 400
    except Exception as e:
        print(f"API错误 - generate: {e}")
        return jsonify({"error": f"生成许可证文件失败: {str(e)}"}), 500

@app.route('/api/create-default-license', methods=['POST'])
def create_default_license():
    """API: 创建默认许可证文件（本机硬件ID + 365天）"""
    try:
        # 获取本机硬件ID
        hardware_id = license_logic.get_hardware_id()
        if not hardware_id:
            return jsonify({"error": "无法获取本机硬件ID"}), 500

        print(f"为本机创建默认许可证: {hardware_id[:8]}...")
        
        # 生成许可证内容
        license_content = license_logic.generate_license_content("Local User", hardware_id, 365)
        if not license_content:
            return jsonify({"error": "生成默认许可证内容失败"}), 500

        # 返回文件
        return send_file(
            io.BytesIO(license_content),
            as_attachment=True,
            download_name='license.lic',
            mimetype='application/octet-stream'
        )
    except Exception as e:
        print(f"API错误 - create_default_license: {e}")
        return jsonify({"error": f"创建默认许可证失败: {str(e)}"}), 500

@app.route('/api/validate-license', methods=['POST'])
def validate_license():
    """API: 验证许可证文件（额外功能）"""
    try:
        if 'license_file' not in request.files:
            return jsonify({"error": "没有上传许可证文件"}), 400
        
        license_file = request.files['license_file']
        if license_file.filename == '':
            return jsonify({"error": "没有选择文件"}), 400

        # 读取文件内容
        license_content = license_file.read()
        
        # 这里可以加入许可证验证逻辑
        # 由于原始程序没有验证功能，这里只做基本检查
        if len(license_content) < 10:
            return jsonify({"error": "许可证文件内容无效"}), 400
        
        return jsonify({
            "message": "许可证文件格式正确",
            "file_size": len(license_content),
            "filename": license_file.filename
        })
    except Exception as e:
        print(f"API错误 - validate_license: {e}")
        return jsonify({"error": f"验证许可证文件失败: {str(e)}"}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """API: 系统状态检查"""
    try:
        # 检查许可证生成器是否正常
        test_id = "test123"
        test_content = license_logic.generate_license_content("Test", test_id, 1)
        
        import platform
        status_info = {
            "status": "online",
            "message": "许可证服务正常运行",
            "server_info": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "machine": platform.machine()
            },
            "license_generator": "正常" if test_content else "异常"
        }
        
        return jsonify(status_info)
    except Exception as e:
        print(f"API错误 - status: {e}")
        return jsonify({
            "status": "error",
            "message": f"系统状态检查失败: {str(e)}"
        }), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "API端点不存在"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "不支持的HTTP方法"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "服务器内部错误"}), 500

# CORS 支持（如果需要跨域请求）
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# if __name__ == '__main__':
#     print("QCIAutomate 许可证服务器启动中...")
#     print("服务器地址:")
#     print("   本地访问:  http://127.0.0.1:5000")
#     print("   网络访问: http://0.0.0.0:5000")
#     print("\n可用的API端点:")
#     print("   GET  /                        - 网页界面")
#     print("   GET  /api/get-hardware-id     - 获取本机硬件ID")
#     print("   POST /generate                - 生成许可证文件")
#     print("   POST /api/create-default-license - 创建默认许可证")
#     print("   POST /api/validate-license    - 验证许可证文件")
#     print("   GET  /api/status              - 系统状态")
#     print("="*50)
    
#     # 在本地的 5000 端口启动服务器
#     # host='0.0.0.0' 允许从外部网络访问
#     # threaded=True 让服务器可以同时处理多个请求
#     app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)