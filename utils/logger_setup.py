import logging
import os
import sys
from utils.config_reader import ConfigReader

class LoggerManager:
    _main_logger = None

    @staticmethod
    def setup_main_logger():
  
        if LoggerManager._main_logger:
            return LoggerManager._main_logger

        log_level_str = ConfigReader.get_value("Logging.Level", "INFO")
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        logger = logging.getLogger("app")
        logger.setLevel(log_level)
        logger.handlers.clear()  # clean old handlers 
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console
        if ConfigReader.get_value("Logging.ConsoleOutput", True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File run.log
        if ConfigReader.get_value("Logging.FileOutput", True):
            log_dir = os.path.join(ConfigReader.get_base_dir(), "Logs") 
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(
                os.path.join(log_dir, "run.log"), 
                mode='w', 
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        LoggerManager._main_logger = logger
        return logger

    @staticmethod
    def get_test_logger(test_name: str):
        logger = logging.getLogger(f"app.{test_name}")
        logger.propagate = ConfigReader.get_value("Logging.Propagate", True)  
        
        log_dir = os.path.join( ConfigReader.get_base_dir(), "Logs", "Tests")  
        os.makedirs(log_dir, exist_ok=True)
        
        log_path = os.path.join(log_dir, f"{test_name}.log")
        
        # clean old handlers 
        if logger.handlers:
            logger.handlers.clear()
        
        file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger, log_path