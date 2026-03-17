import os
import subprocess
import logging
import glob
import time

logger = logging.getLogger("app")

class AllureManager:
    @staticmethod
    def generate_report(results_path, report_path):
        """Generate Allure report using Linux binary (WSL environment)."""
        if not os.path.exists(results_path) or not glob.glob(os.path.join(results_path, "*.json")):
            logger.warning(f"⚠️ Results not found: {results_path}")
            return False

        allure_bin = "/mnt/e/Git_Projects/owasp-juiceshop-vs-project/allure-2.35.1/bin/allure"
        env = os.environ.copy()

        logger.info(f"Generating report from {results_path}...")

        try:
            result = subprocess.run(
                [allure_bin, "generate", results_path, "-o", report_path, "--clean"],
                capture_output=True,
                text=True,
                env=env
            )

            if result.returncode == 0:
                logger.info(f"✅ Report created: {report_path}")
                return True
            else:
                logger.error(f"❌ Allure CLI error:\n{result.stderr}\n{result.stdout}")
                return False
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            return False

    @staticmethod
    def _kill_process_on_port(port: str):
        """Kill any process listening on the given port using fuser."""
        try:

            result = subprocess.run(
                ["fuser", "-k", f"{port}/tcp"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"Killed existing process on port {port}")
                time.sleep(2)  
            else:
                logger.info(f"No process found on port {port}")
        except FileNotFoundError:
            
            logger.warning("fuser not found, trying ss fallback...")
            result = subprocess.run(
                ["ss", "-tlnp", f"sport = :{port}"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "pid=" in line:
                    pid = line.split("pid=")[1].split(",")[0]
                    subprocess.run(["kill", "-9", pid])
                    logger.info(f"Killed PID {pid} on port {port}")
                    time.sleep(2)

    @staticmethod
    def open_report(report_path):
        
        allure_bat = r"E:\Git_Projects\owasp-juiceshop-vs-project\allure-2.35.1\bin\allure.bat"
        port = "4545"
        url = f"http://localhost:{port}"

        if not os.path.exists(report_path):
            logger.error(f"❌ Report path not found: {report_path}")
            return

        try:
            
            AllureManager._kill_process_on_port(port)

            win_path = subprocess.run(
                ["wslpath", "-w", report_path],
                capture_output=True, text=True
            ).stdout.strip()

            logger.info(f"Windows report path: {win_path}")

            subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-Command",
                 f'& "{allure_bat}" open -p {port} "{win_path}"'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            logger.info(f"🚀 Allure server starting on port {port}...")
            time.sleep(8)

            logger.info(f"🌐 Opening browser: {url}")
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", f"Start-Process '{url}'"]
            )
            logger.info(f"✅ Done. If not opened manually: {url}")

        except Exception as e:
            logger.error(f"❌ Failed to open report: {e}")