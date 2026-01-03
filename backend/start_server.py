#!/usr/bin/env python3
import os
import sys
import uvicorn

# Check required environment variables first
required_vars = ["DATABASE_URL", "SECRET_KEY"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8080))
        print(f"Starting server on port {port}...", file=sys.stderr)
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"ERROR starting server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
