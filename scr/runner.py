# main.py
from scr.app_components import app  # This is the same app instance with callbacks already registered

if __name__ == "__main__":
    # Run on all available interfaces, using port 8050.
    app.run_server(debug=True, use_reloader=False, host='0.0.0.0', port=8050)
