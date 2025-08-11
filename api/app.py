from flask import Flask, request, send_file, jsonify, render_template_string
from api.license_generator_web import LicenseGeneratorLogic
import os
import io
import json
import platform

app = Flask(__name__)
license_logic = LicenseGeneratorLogic()

# 读取 HTML 模板文件
# def get_html_template():
#     """读取 HTML 模板文件，如果不存在则返回默认模板"""
#     try:
#         with open('index.html', 'r', encoding='utf-8') as f:
#             return f.read()
#     except FileNotFoundError:
#         # 如果没有 index.html，使用专业的现代化模板
#         return """
# <!DOCTYPE html>
# <html lang="zh-CN">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>QCIAutomate 许可证生成器</title>
#     <style>
#         * {
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }

#         body {
#             font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             min-height: 100vh;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             padding: 20px;
#         }

#         .container {
#             background: rgba(255, 255, 255, 0.95);
#             backdrop-filter: blur(10px);
#             border-radius: 20px;
#             box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
#             padding: 40px;
#             width: 100%;
#             max-width: 800px;
#             animation: slideIn 0.6s ease-out;
#         }

#         @keyframes slideIn {
#             from {
#                 opacity: 0;
#                 transform: translateY(30px);
#             }
#             to {
#                 opacity: 1;
#                 transform: translateY(0);
#             }
#         }

#         .header {
#             text-align: center;
#             margin-bottom: 40px;
#         }

#         .header h1 {
#             font-size: 2.5rem;
#             font-weight: 700;
#             background: linear-gradient(135deg, #667eea, #764ba2);
#             -webkit-background-clip: text;
#             -webkit-text-fill-color: transparent;
#             background-clip: text;
#             margin-bottom: 10px;
#         }

#         .header p {
#             color: #666;
#             font-size: 1.1rem;
#         }

#         .section {
#             background: white;
#             border-radius: 15px;
#             padding: 30px;
#             margin-bottom: 30px;
#             box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
#             transition: transform 0.3s ease, box-shadow 0.3s ease;
#         }

#         .section:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
#         }

#         .section-title {
#             font-size: 1.4rem;
#             font-weight: 600;
#             color: #333;
#             margin-bottom: 20px;
#             display: flex;
#             align-items: center;
#             gap: 10px;
#         }

#         .section-icon {
#             width: 24px;
#             height: 24px;
#             background: linear-gradient(135deg, #667eea, #764ba2);
#             border-radius: 6px;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             color: white;
#             font-weight: bold;
#         }

#         .form-group {
#             margin-bottom: 20px;
#         }

#         .form-label {
#             display: block;
#             margin-bottom: 8px;
#             font-weight: 500;
#             color: #333;
#         }

#         .form-input {
#             width: 100%;
#             padding: 12px 16px;
#             border: 2px solid #e1e5e9;
#             border-radius: 10px;
#             font-size: 16px;
#             transition: all 0.3s ease;
#             background: #f8f9fa;
#         }

#         .form-input:focus {
#             outline: none;
#             border-color: #667eea;
#             background: white;
#             box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
#         }

#         .btn {
#             background: linear-gradient(135deg, #667eea, #764ba2);
#             color: white;
#             border: none;
#             padding: 14px 28px;
#             border-radius: 10px;
#             font-size: 16px;
#             font-weight: 600;
#             cursor: pointer;
#             transition: all 0.3s ease;
#             display: inline-flex;
#             align-items: center;
#             gap: 8px;
#             text-decoration: none;
#             min-width: 160px;
#             justify-content: center;
#         }

#         .btn:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
#         }

#         .btn:active {
#             transform: translateY(0);
#         }

#         .btn-secondary {
#             background: linear-gradient(135deg, #ffecd2, #fcb69f);
#             color: #8b4513;
#         }

#         .btn-secondary:hover {
#             box-shadow: 0 10px 20px rgba(252, 182, 159, 0.3);
#         }

#         .result {
#             margin-top: 20px;
#             padding: 16px;
#             border-radius: 10px;
#             font-weight: 500;
#             opacity: 0;
#             animation: fadeIn 0.5s ease-out forwards;
#         }

#         @keyframes fadeIn {
#             to {
#                 opacity: 1;
#             }
#         }

#         .result.success {
#             background: linear-gradient(135deg, #d4edda, #c3e6cb);
#             color: #155724;
#             border-left: 4px solid #28a745;
#         }

#         .result.error {
#             background: linear-gradient(135deg, #f8d7da, #f5c6cb);
#             color: #721c24;
#             border-left: 4px solid #dc3545;
#         }

#         .loading {
#             display: inline-block;
#             width: 20px;
#             height: 20px;
#             border: 3px solid rgba(255, 255, 255, 0.3);
#             border-radius: 50%;
#             border-top-color: white;
#             animation: spin 1s ease-in-out infinite;
#         }

#         @keyframes spin {
#             to { transform: rotate(360deg); }
#         }

#         .info-grid {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#             gap: 15px;
#             margin-top: 15px;
#         }

#         .info-item {
#             background: #f8f9fa;
#             padding: 12px;
#             border-radius: 8px;
#             border-left: 3px solid #667eea;
#         }

#         .info-label {
#             font-size: 0.85rem;
#             color: #666;
#             margin-bottom: 4px;
#         }

#         .info-value {
#             font-weight: 600;
#             color: #333;
#             word-break: break-all;
#         }

#         .footer {
#             text-align: center;
#             margin-top: 40px;
#             padding-top: 30px;
#             border-top: 1px solid #e1e5e9;
#             color: #666;
#         }

#         @media (max-width: 768px) {
#             .container {
#                 padding: 20px;
#                 margin: 10px;
#             }
            
#             .header h1 {
#                 font-size: 2rem;
#             }
            
#             .section {
#                 padding: 20px;
#             }
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <h1>QCIAutomate 许可证生成器</h1>
#             <p>专业的软件许可证管理系统</p>
#         </div>

#         <div class="section">
#             <div class="section-title">
#                 <div class="section-icon">1</div>
#                 获取本机硬件ID
#             </div>
#             <p style="margin-bottom: 20px; color: #666;">
#                 点击下方按钮获取当前计算机的唯一硬件标识符
#             </p>
#             <button class="btn" onclick="getLocalHardwareId()">
#                 <span id="hardware-btn-text">获取硬件ID</span>
#                 <div id="hardware-loading" class="loading" style="display: none;"></div>
#             </button>
#             <div id="hardware-result"></div>
#         </div>

#         <div class="section">
#             <div class="section-title">
#                 <div class="section-icon">2</div>
#                 生成许可证文件
#             </div>
#             <form id="license-form">
#                 <div class="form-group">
#                     <label class="form-label">客户名称</label>
#                     <input type="text" class="form-input" id="customer_name" value="Local User" required>
#                 </div>
#                 <div class="form-group">
#                     <label class="form-label">硬件ID</label>
#                     <input type="text" class="form-input" id="hardware_id" placeholder="请先获取硬件ID或手动输入" required>
#                 </div>
#                 <div class="form-group">
#                     <label class="form-label">许可证有效期（天）</label>
#                     <input type="number" class="form-input" id="expiry_days" value="365" min="1" max="3650" required>
#                 </div>
#                 <button type="submit" class="btn">
#                     <span id="license-btn-text">生成许可证文件</span>
#                     <div id="license-loading" class="loading" style="display: none;"></div>
#                 </button>
#             </form>
#             <div id="license-result"></div>
#         </div>

#         <div class="section">
#             <div class="section-title">
#                 <div class="section-icon">3</div>
#                 快速生成本机许可证
#             </div>
#             <p style="margin-bottom: 20px; color: #666;">
#                 一键为当前计算机生成默认的365天有效期许可证文件
#             </p>
#             <button class="btn btn-secondary" onclick="createDefaultLicense()">
#                 <span id="default-btn-text">生成本机许可证</span>
#                 <div id="default-loading" class="loading" style="display: none;"></div>
#             </button>
#             <div id="default-result"></div>
#         </div>

#         <div class="footer">
#             <p>QCIAutomate License System v1.0.6</p>
#             <p style="margin-top: 5px; font-size: 0.9rem;">安全可靠的软件许可证管理解决方案</p>
#         </div>
#     </div>

#     <script>
#         function showLoading(buttonId, loadingId, textId) {
#             document.getElementById(textId).style.display = 'none';
#             document.getElementById(loadingId).style.display = 'inline-block';
#             document.getElementById(buttonId.replace('-btn-text', '').replace('-loading', '')).disabled = true;
#         }

#         function hideLoading(buttonId, loadingId, textId) {
#             document.getElementById(textId).style.display = 'inline';
#             document.getElementById(loadingId).style.display = 'none';
#             document.getElementById(buttonId.replace('-btn-text', '').replace('-loading', '')).disabled = false;
#         }

#         async function getLocalHardwareId() {
#             const resultDiv = document.getElementById('hardware-result');
#             showLoading('hardware-btn', 'hardware-loading', 'hardware-btn-text');
            
#             try {
#                 const response = await fetch('/api/get-hardware-id');
#                 const data = await response.json();
                
#                 if (response.ok) {
#                     resultDiv.className = 'result success';
#                     let infoHtml = `
#                         <div style="margin-bottom: 15px;">
#                             <strong>硬件ID获取成功</strong>
#                         </div>
#                         <div class="info-grid">
#                             <div class="info-item">
#                                 <div class="info-label">硬件ID</div>
#                                 <div class="info-value">${data.hardware_id}</div>
#                             </div>
#                             <div class="info-item">
#                                 <div class="info-label">操作系统</div>
#                                 <div class="info-value">${data.system_info || 'N/A'}</div>
#                             </div>
#                             <div class="info-item">
#                                 <div class="info-label">处理器</div>
#                                 <div class="info-value">${data.processor || 'N/A'}</div>
#                             </div>
#                             <div class="info-item">
#                                 <div class="info-label">机器类型</div>
#                                 <div class="info-value">${data.machine || 'N/A'}</div>
#                             </div>
#                     `;
                    
#                     if (data.os_name) {
#                         infoHtml += `
#                             <div class="info-item">
#                                 <div class="info-label">系统版本</div>
#                                 <div class="info-value">${data.os_name}</div>
#                             </div>
#                         `;
#                     }
                    
#                     if (data.cpu_name) {
#                         infoHtml += `
#                             <div class="info-item">
#                                 <div class="info-label">CPU型号</div>
#                                 <div class="info-value">${data.cpu_name}</div>
#                             </div>
#                         `;
#                     }
                    
#                     if (data.total_memory) {
#                         infoHtml += `
#                             <div class="info-item">
#                                 <div class="info-label">内存容量</div>
#                                 <div class="info-value">${data.total_memory}</div>
#                             </div>
#                         `;
#                     }
                    
#                     infoHtml += '</div>';
#                     resultDiv.innerHTML = infoHtml;
#                     document.getElementById('hardware_id').value = data.hardware_id;
#                 } else {
#                     throw new Error(data.error);
#                 }
#             } catch (error) {
#                 resultDiv.className = 'result error';
#                 resultDiv.innerHTML = '获取硬件ID失败: ' + error.message;
#             } finally {
#                 hideLoading('hardware-btn', 'hardware-loading', 'hardware-btn-text');
#             }
#         }

#         document.getElementById('license-form').addEventListener('submit', async function(e) {
#             e.preventDefault();
#             const resultDiv = document.getElementById('license-result');
#             showLoading('license-btn', 'license-loading', 'license-btn-text');
            
#             const formData = new FormData();
#             formData.append('customer_name', document.getElementById('customer_name').value);
#             formData.append('hardware_id', document.getElementById('hardware_id').value);
#             formData.append('expiry_days', document.getElementById('expiry_days').value);
            
#             try {
#                 const response = await fetch('/generate', {
#                     method: 'POST',
#                     body: formData
#                 });

#                 if (response.ok) {
#                     const blob = await response.blob();
#                     const url = window.URL.createObjectURL(blob);
#                     const a = document.createElement('a');
#                     a.href = url;
#                     a.download = 'license.lic';
#                     a.click();
#                     window.URL.revokeObjectURL(url);

#                     resultDiv.className = 'result success';
#                     resultDiv.innerHTML = `
#                         <div style="margin-bottom: 10px;"><strong>许可证文件生成成功</strong></div>
#                         <div>文件已自动下载到您的计算机</div>
#                         <div style="margin-top: 10px;">
#                             <div class="info-item">
#                                 <div class="info-label">客户名称</div>
#                                 <div class="info-value">${document.getElementById('customer_name').value}</div>
#                             </div>
#                         </div>
#                     `;
#                 } else {
#                     const errorData = await response.json();
#                     throw new Error(errorData.error);
#                 }
#             } catch (error) {
#                 resultDiv.className = 'result error';
#                 resultDiv.innerHTML = '生成许可证失败: ' + error.message;
#             } finally {
#                 hideLoading('license-btn', 'license-loading', 'license-btn-text');
#             }
#         });

#         async function createDefaultLicense() {
#             const resultDiv = document.getElementById('default-result');
#             showLoading('default-btn', 'default-loading', 'default-btn-text');
            
#             try {
#                 const response = await fetch('/api/create-default-license', {
#                     method: 'POST'
#                 });

#                 if (response.ok) {
#                     const blob = await response.blob();
#                     const url = window.URL.createObjectURL(blob);
#                     const a = document.createElement('a');
#                     a.href = url;
#                     a.download = 'license.lic';
#                     a.click();
#                     window.URL.revokeObjectURL(url);

#                     resultDiv.className = 'result success';
#                     resultDiv.innerHTML = `
#                         <div style="margin-bottom: 10px;"><strong>本机许可证创建成功</strong></div>
#                         <div>默认365天有效期的许可证文件已下载</div>
#                         <div style="margin-top: 10px; font-size: 0.9rem; color: #666;">
#                             该许可证绑定到当前计算机硬件，仅限本机使用
#                         </div>
#                     `;
#                 } else {
#                     const errorData = await response.json();
#                     throw new Error(errorData.error);
#                 }
#             } catch (error) {
#                 resultDiv.className = 'result error';
#                 resultDiv.innerHTML = '创建本机许可证失败: ' + error.message;
#             } finally {
#                 hideLoading('default-btn', 'default-loading', 'default-btn-text');
#             }
#         }

#         // 页面加载完成后的初始化
#         document.addEventListener('DOMContentLoaded', function() {
#             // 可以在这里添加页面初始化逻辑
#             console.log('QCIAutomate License Generator 已加载');
#         });
#     </script>
# </body>
# </html>
#         """

# @app.route('/')
# def home():
#     """首页，显示硬件ID输入表单"""
#     return get_html_template()
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