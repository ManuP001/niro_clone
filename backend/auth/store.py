"""User and profile storage abstraction"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class UserStore(ABC):
    """Abstract user storage"""
    
    @abstractmethod
    def create_user(self, user_id: str, identifier: str) -> Dict:
        """Create user"""
        pass
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def get_user_by_identifier(self, identifier: str) -> Optional[Dict]:
        """Get user by email/phone"""
        pass


class ProfileStore(ABC):
    """Abstract profile storage"""
    
    @abstractmethod
    def save_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Save user profile"""
        pass
    
    @abstractmethod
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        pass


class InMemoryUserStore(UserStore):
    """In-memory user storage"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.identifier_map: Dict[str, str] = {}  # identifier -> user_id
    
    def create_user(self, user_id: str, identifier: str) -> Dict:
        """Create user in memory"""
        user = {
            'id': user_id,
            'identifier': identifier,
            'created_at': datetime.utcnow().isoformat()
        }
        self.users[user_id] = user
        self.identifier_map[identifier] = user_id
        logger.info(f"[STORE] User created: {user_id} ({identifier})")
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_identifier(self, identifier: str) -> Optional[Dict]:
        """Get user by identifier"""
        user_id = self.identifier_map.get(identifier)
        if user_id:
            return self.users.get(user_id)
        return None


class InMemoryProfileStore(ProfileStore):
    """In-memory profile storage"""
    
    def __init__(self):
        self.profiles: Dict[str, Dict] = {}
    
    def save_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Save profile in memory"""
        self.profiles[user_id] = {
            **profile_data,
            'updated_at': datetime.utcnow().isoformat()
        }
        logger.info(f"[STORE] Profile saved for user: {user_id}")
        return True
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get profile"""
        return self.profiles.get(user_id)


class FileUserStore(UserStore):
    """File-based user storage (fallback)"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir) / 'users'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.identifier_map: Dict[str, str] = {}
        self._load_identifier_map()
    
    def _load_identifier_map(self):
        """Load identifier map from files"""
        for user_file in self.data_dir.glob('*.json'):
            try:
                with open(user_file) as f:
                    user = json.load(f)
                    self.identifier_map[user['identifier']] = user['id']
            except Exception as e:
                logger.error(f"Error loading user file {user_file}: {e}")
    
    def create_user(self, user_id: str, identifier: str) -> Dict:
        """Create user in file storage"""
        user = {
            'id': user_id,
            'identifier': identifier,
            'created_at': datetime.utcnow().isoformat()
        }
        
        user_file = self.data_dir / f"{user_id}.json"
        with open(user_file, 'w') as f:
            json.dump(user, f)
        
        self.identifier_map[identifier] = user_id
        logger.info(f"[STORE] User created (file): {user_id}")
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user from file"""
        try:
            user_file = self.data_dir / f"{user_id}.json"
            with open(user_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def get_user_by_identifier(self, identifier: str) -> Optional[Dict]:
        """Get user by identifier"""
        user_id = self.identifier_map.get(identifier)
        if user_id:
            return self.get_user(user_id)
        return None


class FileProfileStore(ProfileStore):
    """File-based profile storage"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir) / 'profiles'
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Save profile to file"""
        try:
            profile_file = self.data_dir / f"{user_id}.json"
            profile = {
                **profile_data,
                'updated_at': datetime.utcnow().isoformat()
            }
            with open(profile_file, 'w') as f:
                json.dump(profile, f)
            logger.info(f"[STORE] Profile saved (file): {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            return False
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get profile from file"""
        try:
            profile_file = self.data_dir / f"{user_id}.json"
            with open(profile_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None


# Factory functions
def get_user_store(store_type: str = 'inmemory') -> UserStore:
    """Get user store based on config"""
    if store_type == 'file':
        return FileUserStore()
    return InMemoryUserStore()


def get_profile_store(store_type: str = 'inmemory') -> ProfileStore:
    """Get profile store based on config"""
    if store_type == 'file':
        return FileProfileStore()
    return InMemoryProfileStore()


# Lazy-initialized singletons
_user_store = None
_profile_store = None


def get_user_store_instance() -> UserStore:
    """Get or create user store"""
    global _user_store
    if _user_store is None:
        store_type = os.environ.get('NIRO_STORE', 'inmemory')
        _user_store = get_user_store(store_type)
    return _user_store


def get_profile_store_instance() -> ProfileStore:
    """Get or create profile store"""
    global _profile_store
    if _profile_store is None:
        store_type = os.environ.get('NIRO_STORE', 'inmemory')
        _profile_store = get_profile_store(store_type)
    return _profile_store
