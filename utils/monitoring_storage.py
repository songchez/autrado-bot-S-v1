import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MonitoringStorage:
    """
    Handles persistent storage for monitoring configurations
    """
    
    def __init__(self, storage_file: str = 'monitoring_data.json'):
        self.storage_file = storage_file
        self.ensure_storage_exists()
    
    def ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        if not os.path.exists(self.storage_file):
            self.save_monitoring_list([])
    
    def load_monitoring_list(self) -> List[Dict]:
        """Load monitoring configurations from storage"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} monitoring configurations")
                return data
        except Exception as e:
            logger.error(f"Error loading monitoring data: {e}")
            return []
    
    def save_monitoring_list(self, monitoring_list: List[Dict]):
        """Save monitoring configurations to storage"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(monitoring_list, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(monitoring_list)} monitoring configurations")
        except Exception as e:
            logger.error(f"Error saving monitoring data: {e}")
            raise
    
    def add_monitoring_config(self, config: Dict) -> bool:
        """Add a new monitoring configuration"""
        monitoring_list = self.load_monitoring_list()
        
        # Check for duplicates
        existing = next((item for item in monitoring_list 
                        if item['ticker'] == config['ticker'] and 
                           item['strategy'] == config['strategy']), None)
        
        if existing:
            logger.warning(f"Monitoring config already exists for {config['ticker']} with {config['strategy']}")
            return False
        
        # Add timestamp if not present
        if 'added_date' not in config:
            config['added_date'] = datetime.now().isoformat()
        
        # Set default status if not present
        if 'status' not in config:
            config['status'] = 'active'
        
        monitoring_list.append(config)
        self.save_monitoring_list(monitoring_list)
        logger.info(f"Added monitoring config for {config['ticker']} with {config['strategy']}")
        return True
    
    def update_monitoring_status(self, ticker: str, strategy: str, status: str) -> bool:
        """Update the status of a monitoring configuration"""
        monitoring_list = self.load_monitoring_list()
        
        for item in monitoring_list:
            if item['ticker'] == ticker and item['strategy'] == strategy:
                old_status = item['status']
                item['status'] = status
                item['last_updated'] = datetime.now().isoformat()
                self.save_monitoring_list(monitoring_list)
                logger.info(f"Updated {ticker} {strategy} status from {old_status} to {status}")
                return True
        
        logger.warning(f"Monitoring config not found for {ticker} with {strategy}")
        return False
    
    def remove_monitoring_config(self, ticker: str, strategy: str) -> bool:
        """Remove a monitoring configuration"""
        monitoring_list = self.load_monitoring_list()
        original_count = len(monitoring_list)
        
        monitoring_list = [item for item in monitoring_list 
                          if not (item['ticker'] == ticker and item['strategy'] == strategy)]
        
        if len(monitoring_list) < original_count:
            self.save_monitoring_list(monitoring_list)
            logger.info(f"Removed monitoring config for {ticker} with {strategy}")
            return True
        
        logger.warning(f"Monitoring config not found for {ticker} with {strategy}")
        return False
    
    def get_active_monitoring_configs(self) -> List[Dict]:
        """Get all active monitoring configurations"""
        monitoring_list = self.load_monitoring_list()
        active_configs = [item for item in monitoring_list if item.get('status') == 'active']
        logger.info(f"Found {len(active_configs)} active monitoring configurations")
        return active_configs
    
    def get_monitoring_by_status(self, status: str) -> List[Dict]:
        """Get monitoring configurations by status"""
        monitoring_list = self.load_monitoring_list()
        filtered_configs = [item for item in monitoring_list if item.get('status') == status]
        return filtered_configs
    
    def update_monitoring_config(self, ticker: str, strategy: str, updates: Dict) -> bool:
        """Update specific fields in a monitoring configuration"""
        monitoring_list = self.load_monitoring_list()
        
        for item in monitoring_list:
            if item['ticker'] == ticker and item['strategy'] == strategy:
                item.update(updates)
                item['last_updated'] = datetime.now().isoformat()
                self.save_monitoring_list(monitoring_list)
                logger.info(f"Updated monitoring config for {ticker} with {strategy}")
                return True
        
        logger.warning(f"Monitoring config not found for {ticker} with {strategy}")
        return False
    
    def bulk_update_status(self, from_status: str, to_status: str) -> int:
        """Bulk update monitoring configurations from one status to another"""
        monitoring_list = self.load_monitoring_list()
        updated_count = 0
        
        for item in monitoring_list:
            if item.get('status') == from_status:
                item['status'] = to_status
                item['last_updated'] = datetime.now().isoformat()
                updated_count += 1
        
        if updated_count > 0:
            self.save_monitoring_list(monitoring_list)
            logger.info(f"Bulk updated {updated_count} configs from {from_status} to {to_status}")
        
        return updated_count
    
    def cleanup_stopped_configs(self) -> int:
        """Remove all stopped monitoring configurations"""
        monitoring_list = self.load_monitoring_list()
        original_count = len(monitoring_list)
        
        monitoring_list = [item for item in monitoring_list if item.get('status') != 'stopped']
        removed_count = original_count - len(monitoring_list)
        
        if removed_count > 0:
            self.save_monitoring_list(monitoring_list)
            logger.info(f"Cleaned up {removed_count} stopped monitoring configurations")
        
        return removed_count
    
    def get_monitoring_stats(self) -> Dict[str, int]:
        """Get statistics about monitoring configurations"""
        monitoring_list = self.load_monitoring_list()
        
        stats = {
            'total': len(monitoring_list),
            'active': 0,
            'paused': 0,
            'stopped': 0,
            'error': 0
        }
        
        for item in monitoring_list:
            status = item.get('status', 'unknown')
            if status in stats:
                stats[status] += 1
        
        return stats