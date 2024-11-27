"""
Setup module for the LLM Prompting Tool.
Handles environment configuration, Google Drive mounting, and directory management.
"""

import os
from typing import List, Dict, Optional
from google.colab import drive
import yaml
import pkg_resources
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SetupManager:
    def __init__(self, base_path: str = "/content/drive/MyDrive/llm_prompting_tool"):
        """
        Initialize the setup manager.
        
        Args:
            base_path (str): Base path in Google Drive where the tool will store its files
        """
        self.base_path = base_path
        self.required_dirs = {
            'prompts': os.path.join(base_path, 'prompts'),
            'outputs': os.path.join(base_path, 'outputs'),
            'src': os.path.join(base_path, 'src')
        }
        self.required_packages = {
            'jinja2': '>=3.0.0',
            'pyyaml': '>=5.1',
            'python-dotenv': '>=0.19.0',
            'requests': '>=2.26.0'
        }

    def mount_drive(self) -> bool:
        """
        Mount Google Drive if not already mounted.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists('/content/drive'):
                drive.mount('/content/drive')
                logger.info("Google Drive mounted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to mount Google Drive: {str(e)}")
            return False

    def create_directory_structure(self) -> Dict[str, bool]:
        """
        Create the required directory structure if it doesn't exist.
        
        Returns:
            Dict[str, bool]: Dictionary with directory paths and their creation status
        """
        results = {}
        for dir_name, dir_path in self.required_dirs.items():
            try:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    logger.info(f"Created directory: {dir_path}")
                results[dir_name] = True
            except Exception as e:
                logger.error(f"Failed to create directory {dir_path}: {str(e)}")
                results[dir_name] = False
        return results

    def validate_environment(self) -> Dict[str, bool]:
        """
        Validate that all required packages are installed with correct versions.
        
        Returns:
            Dict[str, bool]: Dictionary with package names and their validation status
        """
        validation_results = {}
        for package, version in self.required_packages.items():
            try:
                pkg_resources.require(f"{package}{version}")
                validation_results[package] = True
                logger.info(f"Package {package} validated successfully")
            except (pkg_resources.VersionConflict, pkg_resources.DistributionNotFound) as e:
                validation_results[package] = False
                logger.error(f"Package validation failed for {package}: {str(e)}")
        return validation_results

    def verify_setup(self) -> Dict[str, bool]:
        """
        Verify the complete setup by checking drive mounting, directories, and environment.
        
        Returns:
            Dict[str, bool]: Dictionary with verification results for each component
        """
        results = {
            'drive_mounted': self.mount_drive(),
            'directories': all(self.create_directory_structure().values()),
            'environment': all(self.validate_environment().values())
        }
        
        if all(results.values()):
            logger.info("Setup verification completed successfully")
        else:
            logger.warning("Setup verification completed with issues")
            
        return results

    def get_config_path(self) -> str:
        """
        Get the path to the configuration file.
        
        Returns:
            str: Path to the configuration file
        """
        return os.path.join(self.base_path, 'config.yaml')

    def save_config(self, config: Dict) -> bool:
        """
        Save configuration to a YAML file.
        
        Args:
            config (Dict): Configuration dictionary to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_path = self.get_config_path()
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
            logger.info(f"Configuration saved to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False

    def load_config(self) -> Optional[Dict]:
        """
        Load configuration from YAML file.
        
        Returns:
            Optional[Dict]: Configuration dictionary if successful, None otherwise
        """
        try:
            config_path = self.get_config_path()
            if not os.path.exists(config_path):
                logger.warning("Configuration file does not exist")
                return None
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return None 