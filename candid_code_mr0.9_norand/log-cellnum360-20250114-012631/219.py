# Import anything you need below
import hashlib
import time

# Put tunable constant parameters below
CONSISTENCY_SCORE_DEFAULT = 1.0
WEIGHT_ACCESS_FREQUENCY = 0.4
WEIGHT_LAST_ACCESS = 0.3
WEIGHT_CONSISTENCY_SCORE = 0.2
WEIGHT_DATA_INTEGRITY = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, data integrity hash, and consistency score for each cache entry.
metadata = {
    'access_frequency': {},
    'last_access_timestamp': {},
    'data_integrity_hash': {},
    'consistency_score': {}
}

def calculate_data_integrity_hash(obj):
    return hashlib.md5(obj.key.encode()).hexdigest()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score combining low access frequency, old last access timestamp, low consistency score, and data integrity check failures.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'].get(key, 0)
        last_access_timestamp = metadata['last_access_timestamp'].get(key, 0)
        consistency_score = metadata['consistency_score'].get(key, CONSISTENCY_SCORE_DEFAULT)
        data_integrity_hash = metadata['data_integrity_hash'].get(key, '')

        # Calculate the weighted score
        score = (WEIGHT_ACCESS_FREQUENCY * (1 / (access_frequency + 1)) +
                 WEIGHT_LAST_ACCESS * (cache_snapshot.access_count - last_access_timestamp) +
                 WEIGHT_CONSISTENCY_SCORE * (1 / (consistency_score + 1)) +
                 WEIGHT_DATA_INTEGRITY * (1 if data_integrity_hash != calculate_data_integrity_hash(cached_obj) else 0))
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access timestamp to the current time, recalculates the data integrity hash, and adjusts the consistency score based on the temporal alignment protocol.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['data_integrity_hash'][key] = calculate_data_integrity_hash(obj)
    metadata['consistency_score'][key] = CONSISTENCY_SCORE_DEFAULT  # Adjust based on temporal alignment protocol

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, computes the initial data integrity hash, and assigns a default consistency score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['data_integrity_hash'][key] = calculate_data_integrity_hash(obj)
    metadata['consistency_score'][key] = CONSISTENCY_SCORE_DEFAULT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted entry and recalibrates the consistency mapping for the remaining entries to ensure balanced temporal alignment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_timestamp']:
        del metadata['last_access_timestamp'][evicted_key]
    if evicted_key in metadata['data_integrity_hash']:
        del metadata['data_integrity_hash'][evicted_key]
    if evicted_key in metadata['consistency_score']:
        del metadata['consistency_score'][evicted_key]
    
    # Recalibrate consistency mapping for remaining entries
    for key in metadata['consistency_score']:
        metadata['consistency_score'][key] = CONSISTENCY_SCORE_DEFAULT  # Adjust based on temporal alignment protocol