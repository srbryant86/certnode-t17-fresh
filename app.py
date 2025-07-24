#!/usr/bin/env python3
"""
CertNode T17+ Logic Governance Infrastructure
Web Interface for the Complete T17+ System

This integrates Claude's complete T17+ system with a proper web interface
that provides the same functionality as the CLI but through a web browser.
"""

import os
import sys
from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import json
import traceback

# Import the complete T17+ system components from Claude
from certnode_config import CertNodeConfig
from certnode_main import CertNodeMain
from certnode_api import CertNodeAPI
from certnode_processor import CertificationRequest

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the complete T17+ system
certnode_main = CertNodeMain()
certnode_api = CertNodeAPI()

# Professional web interface template
WEB_INTERFACE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CertNode T17+ Logic Governance Infrastructure</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white; 
            padding: 40px; 
            text-align: center; 
        }
        .logo { font-size: 48px; margin-bottom: 10px; }
        .title { font-size: 32px; font-weight: 300; margin-bottom: 10px; }
        .subtitle { font-size: 18px; opacity: 0.9; margin-bottom: 20px; }
        .version { 
            background: rgba(255,255,255,0.2); 
            padding: 8px 16px; 
            border-radius: 20px; 
            display: inline-block; 
            font-size: 14px; 
        }
        
        .main-content { padding: 40px; }
        .certification-form { 
            background: #f8f9fa; 
            padding: 30px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #2c3e50; 
        }
        .form-control { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e9ecef; 
            border-radius: 8px; 
            font-size: 16px; 
            transition: border-color 0.3s; 
        }
        .form-control:focus { 
            outline: none; 
            border-color: #667eea; 
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); 
        }
        textarea.form-control { 
            min-height: 200px; 
            resize: vertical; 
            font-family: 'Courier New', monospace; 
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 8px; 
            font-size: 16px; 
            font-weight: 600; 
            cursor: pointer; 
            transition: transform 0.2s; 
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none; 
        }
        
        .results { 
            margin-top: 30px; 
            padding: 30px; 
            background: #f8f9fa; 
            border-radius: 10px; 
            display: none; 
        }
        .results.show { display: block; }
        .result-success { 
            border-left: 5px solid #28a745; 
            background: #d4edda; 
            color: #155724; 
        }
        .result-failure { 
            border-left: 5px solid #dc3545; 
            background: #f8d7da; 
            color: #721c24; 
        }
        .result-header { 
            font-size: 24px; 
            font-weight: 600; 
            margin-bottom: 20px; 
        }
        .result-details { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }
        .detail-card { 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .detail-label { 
            font-weight: 600; 
            color: #6c757d; 
            margin-bottom: 5px; 
        }
        .detail-value { 
            font-size: 18px; 
            color: #2c3e50; 
        }
        
        .system-status { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .status-card { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
        }
        .status-icon { font-size: 32px; margin-bottom: 10px; }
        .status-label { font-weight: 600; color: #6c757d; }
        .status-value { font-size: 20px; color: #2c3e50; margin-top: 5px; }
        
        .loading { 
            display: none; 
            text-align: center; 
            padding: 20px; 
        }
        .loading.show { display: block; }
        .spinner { 
            border: 4px solid #f3f3f3; 
            border-top: 4px solid #667eea; 
            border-radius: 50%; 
            width: 40px; 
            height: 40px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto 20px; 
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .api-endpoints { 
            background: #f8f9fa; 
            padding: 30px; 
            border-radius: 10px; 
            margin-top: 30px; 
        }
        .endpoint { 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            border-left: 4px solid #667eea; 
        }
        .endpoint-method { 
            font-weight: 600; 
            color: #667eea; 
            margin-right: 10px; 
        }
        .endpoint-path { 
            font-family: 'Courier New', monospace; 
            background: #e9ecef; 
            padding: 4px 8px; 
            border-radius: 4px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🏛️</div>
            <div class="title">CertNode T17+ Logic Governance Infrastructure</div>
            <div class="subtitle">Institutional-Grade Automated Logic Analysis & Certification</div>
            <div class="version">T17+ v2.0.0 | Operator: {{ operator }}</div>
        </div>
        
        <div class="main-content">
            <!-- System Status -->
            <div class="system-status">
                <div class="status-card">
                    <div class="status-icon">⚡</div>
                    <div class="status-label">System Status</div>
                    <div class="status-value">Operational</div>
                </div>
                <div class="status-card">
                    <div class="status-icon">🔒</div>
                    <div class="status-label">Vault Status</div>
                    <div class="status-value">{{ vault_status }}</div>
                </div>
                <div class="status-card">
                    <div class="status-icon">📊</div>
                    <div class="status-label">Certifications</div>
                    <div class="status-value">{{ cert_count }}</div>
                </div>
                <div class="status-card">
                    <div class="status-icon">🎯</div>
                    <div class="status-label">Threshold</div>
                    <div class="status-value">{{ threshold }}</div>
                </div>
            </div>
            
            <!-- Certification Form -->
            <div class="certification-form">
                <h2>Content Certification</h2>
                <p>Submit content for T17+ Logic Governance analysis and certification.</p>
                
                <form id="certificationForm">
                    <div class="form-group">
                        <label for="content">Content to Certify</label>
                        <textarea id="content" name="content" class="form-control" 
                                placeholder="Enter the content you want to certify (minimum 100 characters)..." 
                                required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="title">Title (Optional)</label>
                        <input type="text" id="title" name="title" class="form-control" 
                               placeholder="Enter a title for this content">
                    </div>
                    
                    <div class="form-group">
                        <label for="cert_type">Certification Type</label>
                        <select id="cert_type" name="cert_type" class="form-control">
                            <option value="LOGIC_FRAGMENT">Logic Fragment</option>
                            <option value="FULL_DOCUMENT">Full Document</option>
                            <option value="RESEARCH_PAPER">Research Paper</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="author_id">Author ID (Optional)</label>
                        <input type="text" id="author_id" name="author_id" class="form-control" 
                               placeholder="Enter author identifier">
                    </div>
                    
                    <button type="submit" class="btn">🔍 Analyze & Certify</button>
                </form>
            </div>
            
            <!-- Loading Indicator -->
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Processing through T17+ Logic Governance Pipeline...</p>
                <p><small>CDP → FRAME → STRIDE → ICS → VAULT</small></p>
            </div>
            
            <!-- Results -->
            <div id="results" class="results">
                <div id="resultContent"></div>
            </div>
            
            <!-- API Endpoints -->
            <div class="api-endpoints">
                <h3>Available API Endpoints</h3>
                <div class="endpoint">
                    <span class="endpoint-method">POST</span>
                    <span class="endpoint-path">/api/v1/certify</span>
                    <span> - Certify content through T17+ pipeline</span>
                </div>
                <div class="endpoint">
                    <span class="endpoint-method">POST</span>
                    <span class="endpoint-path">/api/v1/verify</span>
                    <span> - Verify content against certification</span>
                </div>
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <span class="endpoint-path">/api/v1/status</span>
                    <span> - Get system status and statistics</span>
                </div>
                <div class="endpoint">
                    <span class="endpoint-method">GET</span>
                    <span class="endpoint-path">/health</span>
                    <span> - Health check endpoint</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('certificationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                content: formData.get('content'),
                title: formData.get('title'),
                cert_type: formData.get('cert_type'),
                author_id: formData.get('author_id')
            };
            
            // Validate content length
            if (data.content.length < 100) {
                alert('Content must be at least 100 characters long.');
                return;
            }
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            
            try {
                const response = await fetch('/api/v1/certify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                // Hide loading
                document.getElementById('loading').classList.remove('show');
                
                // Show results
                displayResults(result, response.ok);
                
            } catch (error) {
                document.getElementById('loading').classList.remove('show');
                displayError('Network error: ' + error.message);
            }
        });
        
        function displayResults(result, success) {
            const resultsDiv = document.getElementById('results');
            const contentDiv = document.getElementById('resultContent');
            
            resultsDiv.className = 'results show ' + (success ? 'result-success' : 'result-failure');
            
            let html = `
                <div class="result-header">
                    ${success ? '✅ Certification Successful' : '❌ Certification Failed'}
                </div>
                
                <div class="result-details">
                    <div class="detail-card">
                        <div class="detail-label">Certificate ID</div>
                        <div class="detail-value">${result.cert_id || 'N/A'}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">Score</div>
                        <div class="detail-value">${result.certification_score}</div>
                    </div>
                    <div class="detail-card">
                        <div class="detail-label">Processing Time</div>
                        <div class="detail-value">${result.processing_time}s</div>
                    </div>
            `;
            
            if (result.ics_hash) {
                html += `
                    <div class="detail-card">
                        <div class="detail-label">ICS Hash</div>
                        <div class="detail-value" style="font-family: monospace; font-size: 14px;">${result.ics_hash}</div>
                    </div>
                `;
            }
            
            html += '</div>';
            
            if (result.issues && result.issues.length > 0) {
                html += '<h4>Issues Identified:</h4><ul>';
                result.issues.forEach(issue => {
                    html += `<li>${issue}</li>`;
                });
                html += '</ul>';
            }
            
            if (result.recommendations && result.recommendations.length > 0) {
                html += '<h4>Recommendations:</h4><ul>';
                result.recommendations.forEach(rec => {
                    html += `<li>${rec}</li>`;
                });
                html += '</ul>';
            }
            
            contentDiv.innerHTML = html;
        }
        
        function displayError(message) {
            const resultsDiv = document.getElementById('results');
            const contentDiv = document.getElementById('resultContent');
            
            resultsDiv.className = 'results show result-failure';
            contentDiv.innerHTML = `
                <div class="result-header">❌ Error</div>
                <p>${message}</p>
            `;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main web interface."""
    try:
        # Get system status from the complete T17+ system
        vault_status = "Available" if certnode_main.vault.is_available() else "Unavailable"
        cert_count = certnode_main.vault.get_certification_count()
        
        return render_template_string(WEB_INTERFACE_TEMPLATE,
            operator=certnode_main.config.OPERATOR,
            vault_status=vault_status,
            cert_count=cert_count,
            threshold=certnode_main.config.CERTIFICATION_THRESHOLD
        )
    except Exception as e:
        return jsonify({
            "error": "System initialization failed",
            "message": str(e)
        }), 500

@app.route('/certify', methods=['POST'])
def web_certify():
    """Web interface certification endpoint."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Content required"}), 400
        
        # Use the complete T17+ system for certification
        success = certnode_main.detailed_certify(
            content=data['content'],
            cert_type=data.get('cert_type', 'LOGIC_FRAGMENT'),
            author_id=data.get('author_id'),
            title=data.get('title'),
            export_badges=True
        )
        
        return jsonify({
            "success": success,
            "message": "Certification completed" if success else "Certification failed"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Certification failed",
            "message": str(e)
        }), 500

# Mount the complete API server routes
@app.route('/api/v1/certify', methods=['POST'])
def api_certify():
    """Proxy to complete API server."""
    return certnode_api.certify_content()

@app.route('/api/v1/verify', methods=['POST'])
def api_verify():
    """Proxy to complete API server."""
    return certnode_api.verify_content()

@app.route('/api/v1/verify/<ics_hash>', methods=['GET'])
def api_verify_hash(ics_hash):
    """Proxy to complete API server."""
    return certnode_api.verify_by_hash(ics_hash)

@app.route('/api/v1/status', methods=['GET'])
def api_status():
    """Proxy to complete API server."""
    return certnode_api.get_status()

@app.route('/api/v1/vault/stats', methods=['GET'])
def api_vault_stats():
    """Proxy to complete API server."""
    return certnode_api.get_vault_stats()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return certnode_api.health_check()

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 10000))
        print(f"🏛️ CertNode T17+ Logic Governance Infrastructure")
        print(f"🚀 Starting web interface on port {port}")
        print(f"🔧 Complete system integration active")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        traceback.print_exc()

