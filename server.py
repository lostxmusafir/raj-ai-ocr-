"""
Laser Cut Metal Stencil OCR - Dedicated Backend API Server
Runs the REST API for Mobile (Android Kotlin/Java), iOS, and Web clients.
"""
import os
import sys

# Ensure current directory is on sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from api.index import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 65)
    print(" ⚡ LASER CUT METAL STENCIL OCR - BACKEND API SERVER")
    print("=" * 65)
    print(f" [OK] Server running on:  http://0.0.0.0:{port}")
    print(f" [OK] Health Check:       GET  http://localhost:{port}/health")
    print(f" [OK] OCR Upload:         POST http://localhost:{port}/ocr  (or /api/ocr)")
    print(f" [OK] Model Catalog:      GET  http://localhost:{port}/catalog")
    print("=" * 65)
    print(" Ready to receive image uploads from Mobile / Kotlin / Java clients.")
    app.run(host='0.0.0.0', port=port, debug=False)
