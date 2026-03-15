import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env into (os.environ)
load_dotenv()

class ConfigReader:
    """
The class implements priority (Data-Driven):
1. Environment variables / .env (high priority)
2. appsettings.json (default values)
    """
    
    _config = None

    @staticmethod
    def _get_config():
        if ConfigReader._config is None:
            
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, 'config', 'appsettings.json')
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    ConfigReader._config = json.load(f)
            except FileNotFoundError:
                print(f" Config file doesn't found in path: {config_path}")
                ConfigReader._config = {}
        return ConfigReader._config

    @staticmethod
    def get_value(key_path, default=None):
        """
        Retrieval priority:
        1. Environment variable (e.g., BROWSERSETTINGS_HEADLESS)
        2. Value from appsettings.json (BrowserSettings.Headless)
        3. Default value
        """
        # 1. Check Environment Variables / .env
        # move "BrowserSettings.Headless" -> "BROWSERSETTINGS_HEADLESS"
        env_key = key_path.replace('.', '_').upper()
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            # Adopt (bool, int)
            if env_value.lower() in ('true', '1'): return True
            if env_value.lower() in ('false', '0'): return False
            try:
                if '.' in env_value: return float(env_value)
                return int(env_value)
            except ValueError:
                return env_value

        # 2. Search in appsettings JSON
        keys = key_path.split('.')
        data = ConfigReader._get_config()
        
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                data = None
                break
        
        return data if data is not None else default
    

    @staticmethod
    def get_full_path(path_key):

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_dir = ConfigReader.get_value("Paths.BaseReportDir", "reports")
        sub_dir = ConfigReader.get_value(f"Paths.{path_key}", path_key.lower())
        
        full_path = os.path.join(project_root, base_dir, sub_dir)
        
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            
        return full_path

    @staticmethod
    def get_log_file_path():
        logs_dir = ConfigReader.get_full_path("Logs")
        file_name = ConfigReader.get_value("Paths.LogFileName", "automation.log")
        return os.path.join(logs_dir, file_name)
    
    @staticmethod
    def get_browser():
        return ConfigReader.get_value("BrowserSettings.DefaultBrowser", "chrom")  
    
    @staticmethod
    def get_headless():
        return ConfigReader.get_value("BrowserSettings.Headless", True)  