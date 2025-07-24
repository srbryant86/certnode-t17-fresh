#!/usr/bin/env python3
"""
CertNode T17+ Logic Governance Infrastructure
Main Flask Application Entry Point

This is the complete T17+ system with all 21 components integrated.
"""

import os
import sys
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime
import json

# Import T17+ system components
from certnode_config import CertNodeConfig
from certnode_api import CertNodeAPI
from certnode_processor import CertNodeProcessor
from vault_manager import VaultManager

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize T17+ components
config = CertNodeConfig()
vault = VaultManager()
processor = CertNodeProcessor()
api = CertNodeAPI()

# HTML template for the main interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ system_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { text-align: center; background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .logo { font-size: 48px; margin-bottom: 10px; }
        .title { font-size: 28px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .subtitle { font-size: 18px; color: #666; margin-bottom: 20px; }
        .version { font-size: 16px; color: #888; }
        .endpoints { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .endpoint { margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
        .method { font-weight: bold; color: #007bff; }
        .path { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
        .description { color: #666; margin-top: 5px; }
        .t17-badge { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; display: inline-block; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🔒</div>
        <div class="title">{{ system_name }}</div>
        <div class="subtitle">{{ subtitle }}</div>
        <div class="t17-badge">T17+ Logic Governance Infrastructure</div>
        <div class="version">{{ version }} | {{ operator }}</div>
    </div>
    
    <div class="endpoints">
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <div><span class="method">POST</span> <span class="path">/api/v1/certify</span></div>
            <div class="description">Certify content with T17+ logic governance analysis</div>
        </div>
        
        <div class="endpoint">
            <div><span class="method">GET</span> <span class="path">/api/v1/verify/{cert_id}</span></div>
            <div class="description">Verify a certification by ID</div>
        </div>
        
        <div class="endpoint">
            <div><span class="method">GET</span> <span class="path">/api/v1/status</span></div>
            <div class="description">System status and statistics</div>
        </div>
        
        <div class="endpoint">
            <div><span class="method">GET</span> <span class="path">/health</span></div>
            <div class="description">System health check</div>
        </div>
        
        <div class="endpoint">
            <div><span class="method">POST</span> <span class="path">/api/v1/badge</span></div>
            <div class="description">Generate certification badge</div>
        </div>
        
        <div class="endpoint">
            <div><span class="method">GET</span> <span class="path">/api/v1/vault</span></div>
            <div class="description">Access certification vault</div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main interface for T17+ system."""
    return render_template_string(HTML_TEMPLATE,
        system_name=config.SYSTEM_NAME,
        subtitle="Institutional-Grade Logic Certification System",
        version=config.CERTNODE_VERSION,
        operator=config.OPERATOR
    )

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "operational",
        "system": config.SYSTEM_NAME,
        "version": config.CERTNODE_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "vault": "operational",
            "processor": "operational",
            "api": "operational"
        }
    })

@app.route('/api/v1/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        "system": config.SYSTEM_NAME,
        "version": config.CERTNODE_VERSION,
        "operator": config.OPERATOR,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "stats": {
            "total_certifications": vault.get_certification_count(),
            "supported_types": list(config.CERT_TYPES.keys()),
            "last_certification": vault.get_last_certification_time()
        }
    })

@app.route('/api/v1/certify', methods=['POST'])
def certify():
    """Certify content using T17+ logic governance."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Content required"}), 400
        
        # Process through T17+ pipeline
        result = processor.process_certification(data['content'], data.get('type', 'LOGIC_FRAGMENT'))
        
        # Store in vault
        cert_id = vault.store_certification(result)
        result['certification_id'] = cert_id
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/verify/<cert_id>')
def verify(cert_id):
    """Verify a certification by ID."""
    try:
        certification = vault.get_certification(cert_id)
        if not certification:
            return jsonify({"error": "Certification not found"}), 404
        return jsonify(certification)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/badge', methods=['POST'])
def generate_badge():
    """Generate certification badge."""
    try:
        data = request.get_json()
        if not data or 'cert_id' not in data:
            return jsonify({"error": "Certification ID required"}), 400
        
        badge = api.generate_badge(data['cert_id'])
        return jsonify(badge)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/vault')
def vault_info():
    """Get vault information."""
    try:
        info = vault.get_vault_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize vault
    vault.initialize()
    
    # Get port from environment (Render uses PORT)
    port = int(os.environ.get('PORT', 8000))
    
    # Run the T17+ system
    print(f"🚀 Starting {config.SYSTEM_NAME}")
    print(f"🔒 Version: {config.CERTNODE_VERSION}")
    print(f"🌐 Port: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)

