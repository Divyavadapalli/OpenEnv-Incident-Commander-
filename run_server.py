#!/usr/bin/env python
"""
Direct server startup script - runs uvicorn programmatically.
This avoids shell path issues with background terminals.
"""

import os
import sys

# Set working directory to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    print(f"✓ Working directory: {os.getcwd()}")
    print("✓ Starting IncidentCommander server...")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
        log_level="info"
    )
