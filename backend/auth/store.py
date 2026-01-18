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


class MongoUserStore(UserStore):
    """MongoDB-based user storage with lazy connection and graceful error handling"""
    
    def __init__(self):
        self._client = None
        self._db = None
        self._collection = None
        self._connection_failed = False
        self._fallback_store = InMemoryUserStore()  # Fallback for errors
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'niro_ai_db')
        logger.info(f"[STORE] MongoDB user store created (lazy init): {self.db_name}")
    
    def _get_collection(self):
        """Lazy connection to MongoDB - only connects when first needed"""
        if self._connection_failed:
            return None
        
        if self._collection is None:
            try:
                from pymongo import MongoClient
                from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
                
                # Short timeout to fail fast
                self._client = MongoClient(
                    self.mongo_url,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=5000
                )
                # Test the connection
                self._client.admin.command('ping')
                self._db = self._client[self.db_name]
                self._collection = self._db['auth_users']
                logger.info(f"[STORE] MongoDB user store connected successfully: {self.db_name}")
            except Exception as e:
                logger.warning(f"[STORE] MongoDB connection failed, using fallback: {e}")
                self._connection_failed = True
                return None
        
        return self._collection
    
    def create_user(self, user_id: str, identifier: str) -> Dict:
        """Create user in MongoDB with fallback"""
        collection = self._get_collection()
        
        if collection is None:
            logger.info(f"[STORE] Using fallback for create_user: {user_id}")
            return self._fallback_store.create_user(user_id, identifier)
        
        try:
            user = {
                'user_id': user_id,
                'identifier': identifier,
                'created_at': datetime.utcnow().isoformat()
            }
            collection.update_one(
                {'user_id': user_id},
                {'$set': user},
                upsert=True
            )
            logger.info(f"[STORE] User created (mongo): {user_id} ({identifier})")
            return {'id': user_id, 'identifier': identifier, 'created_at': user['created_at']}
        except Exception as e:
            logger.error(f"Error creating user in MongoDB, using fallback: {e}")
            return self._fallback_store.create_user(user_id, identifier)
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID from MongoDB with fallback"""
        collection = self._get_collection()
        
        if collection is None:
            return self._fallback_store.get_user(user_id)
        
        try:
            doc = collection.find_one({'user_id': user_id}, {'_id': 0})
            if doc:
                return {'id': doc['user_id'], 'identifier': doc.get('identifier'), 'created_at': doc.get('created_at')}
            # Also check fallback in case data was stored there during an outage
            return self._fallback_store.get_user(user_id)
        except Exception as e:
            logger.error(f"Error getting user from MongoDB: {e}")
            return self._fallback_store.get_user(user_id)
    
    def get_user_by_identifier(self, identifier: str) -> Optional[Dict]:
        """Get user by identifier from MongoDB with fallback"""
        collection = self._get_collection()
        
        if collection is None:
            return self._fallback_store.get_user_by_identifier(identifier)
        
        try:
            doc = collection.find_one({'identifier': identifier}, {'_id': 0})
            if doc:
                return {'id': doc['user_id'], 'identifier': doc.get('identifier'), 'created_at': doc.get('created_at')}
            # Also check fallback
            return self._fallback_store.get_user_by_identifier(identifier)
        except Exception as e:
            logger.error(f"Error getting user by identifier from MongoDB: {e}")
            return self._fallback_store.get_user_by_identifier(identifier)


class MongoProfileStore(ProfileStore):
    """MongoDB-based profile storage with lazy connection and graceful error handling"""
    
    def __init__(self):
        self._client = None
        self._db = None
        self._collection = None
        self._connection_failed = False
        self._fallback_store = InMemoryProfileStore()  # Fallback for errors
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'niro_ai_db')
        logger.info(f"[STORE] MongoDB profile store created (lazy init): {self.db_name}")
    
    def _get_collection(self):
        """Lazy connection to MongoDB - only connects when first needed"""
        if self._connection_failed:
            return None
        
        if self._collection is None:
            try:
                from pymongo import MongoClient
                from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
                
                # Short timeout to fail fast
                self._client = MongoClient(
                    self.mongo_url,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
                # Test the connection
                self._client.admin.command('ping')
                self._db = self._client[self.db_name]
                self._collection = self._db['auth_profiles']
                logger.info(f"[STORE] MongoDB profile store connected successfully: {self.db_name}")
            except Exception as e:
                logger.warning(f"[STORE] MongoDB profile connection failed, using fallback: {e}")
                self._connection_failed = True
                return None
        
        return self._collection
    
    def save_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Save profile to MongoDB with fallback"""
        collection = self._get_collection()
        
        if collection is None:
            logger.info(f"[STORE] Using fallback for save_profile: {user_id}")
            return self._fallback_store.save_profile(user_id, profile_data)
        
        try:
            profile = {
                'user_id': user_id,
                **profile_data,
                'updated_at': datetime.utcnow().isoformat()
            }
            collection.update_one(
                {'user_id': user_id},
                {'$set': profile},
                upsert=True
            )
            logger.info(f"[STORE] Profile saved (mongo): {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving profile to MongoDB, using fallback: {e}")
            return self._fallback_store.save_profile(user_id, profile_data)
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get profile from MongoDB with fallback"""
        collection = self._get_collection()
        
        if collection is None:
            return self._fallback_store.get_profile(user_id)
        
        try:
            doc = collection.find_one({'user_id': user_id}, {'_id': 0, 'user_id': 0})
            if doc:
                return doc
            # Also check fallback in case data was stored there during an outage
            return self._fallback_store.get_profile(user_id)
        except Exception as e:
            logger.error(f"Error getting profile from MongoDB: {e}")
            return self._fallback_store.get_profile(user_id)


# Factory functions
def get_user_store(store_type: str = 'mongo') -> UserStore:
    """Get user store based on config"""
    if store_type == 'file':
        return FileUserStore()
    elif store_type == 'inmemory':
        return InMemoryUserStore()
    else:
        # Default to MongoDB for production
        try:
            return MongoUserStore()
        except Exception as e:
            logger.warning(f"Failed to initialize MongoDB user store: {e}, falling back to in-memory")
            return InMemoryUserStore()


def get_profile_store(store_type: str = 'mongo') -> ProfileStore:
    """Get profile store based on config"""
    if store_type == 'file':
        return FileProfileStore()
    elif store_type == 'inmemory':
        return InMemoryProfileStore()
    else:
        # Default to MongoDB for production
        try:
            return MongoProfileStore()
        except Exception as e:
            logger.warning(f"Failed to initialize MongoDB profile store: {e}, falling back to in-memory")
            return InMemoryProfileStore()


# Lazy-initialized singletons
_user_store = None
_profile_store = None


def get_user_store_instance() -> UserStore:
    """Get or create user store"""
    global _user_store
    if _user_store is None:
        store_type = os.environ.get('NIRO_STORE', 'mongo')  # Default to mongo
        _user_store = get_user_store(store_type)
    return _user_store


def get_profile_store_instance() -> ProfileStore:
    """Get or create profile store"""
    global _profile_store
    if _profile_store is None:
        store_type = os.environ.get('NIRO_STORE', 'mongo')  # Default to mongo
        _profile_store = get_profile_store(store_type)
    return _profile_store
