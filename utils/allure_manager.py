import os
import subprocess
import logging
import glob

logger = logging.getLogger("app")

class AllureManager:
    
    allure_bat = r"E:\Git_Projects\owasp-juiceshop-vs-project\allure-2.35.1\bin\allure.bat"
    
    @staticmethod
    def open_report(results_path):
        """Generate and open Allure report in one command."""
        if not os.path.exists(results_path) or not glob.glob(os.path.join(results_path, "*.json")):
            logger.warning(f"⚠️ Results not found: {results_path}")
            return

        win_path = subprocess.run(
            ["wslpath", "-w", results_path],
            capture_output=True, text=True
        ).stdout.strip()

        logger.info(f"🚀 Opening Allure report...")
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-Command",
             f'& "{AllureManager.allure_bat}" serve "{win_path}"'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # subprocess.Popen( # starts a process in the background, doesn't wait for completion
        #     ["powershell.exe", # launches PowerShell
        #     "-NoProfile", # without loading the PowerShell profile (faster)
        #     "-Command", # next argument is the command
        #     f'& "{AllureManager.allure_bat}" serve "{win_path}"']
        #     # & is the call operator in PowerShell
        #     # allure.bat serve is the command that generates + and opens
        #     # win_path is the path to allure-results in Windows format
        #     stdout=subprocess.DEVNULL, # hide the output
        #     stderr=subprocess.DEVNULL # hide errors
        # )