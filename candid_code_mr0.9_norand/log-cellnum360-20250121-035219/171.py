# Import anything you need below
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIMESTAMP = 1.0
WEIGHT_PREDICTED_FUTURE_ACCESS_TIME = 1.0
WEIGHT_DATA_INTEGRITY_SCORE = 1.0
WEIGHT_ACCESS_GRANULARITY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, data integrity score, and access granularity level for each cache entry.
metadata = {
    # Example structure:
    # 'obj_key': {
    #     'access_frequency': 0,
    #     'last_access_timestamp': 0,
    #     'predicted_future_access_time': 0,
    #     'data_integrity_score': 0,
    #     'access_granularity_level': 0
    # }
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that combines the least frequently accessed, the oldest last access timestamp, the furthest predicted future access time, the lowest data integrity score, and the coarsest access granularity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = (
            WEIGHT_ACCESS_FREQUENCY * meta['access_frequency'] +
            WEIGHT_LAST_ACCESS_TIMESTAMP * (cache_snapshot.access_count - meta['last_access_timestamp']) +
            WEIGHT_PREDICTED_FUTURE_ACCESS_TIME * meta['predicted_future_access_time'] +
            WEIGHT_DATA_INTEGRITY_SCORE * meta['data_integrity_score'] +
            WEIGHT_ACCESS_GRANULARITY * meta['access_granularity_level']
        )
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access timestamp to the current time, recalculates the predicted future access time based on recent access patterns, and adjusts the data integrity score and access granularity level if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    meta = metadata[key]
    meta['access_frequency'] += 1
    meta['last_access_timestamp'] = cache_snapshot.access_count
    # Recalculate predicted future access time, data integrity score, and access granularity level if necessary
    # For simplicity, we assume they remain unchanged in this example

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, estimates the predicted future access time based on initial access patterns, assigns a default data integrity score, and sets the access granularity level based on the object's characteristics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'predicted_future_access_time': 0,  # Initial estimate
        'data_integrity_score': 1,  # Default score
        'access_granularity_level': 1  # Default level
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted entry and recalibrates the predicted future access times for remaining entries to ensure optimal latency and integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    # Recalibrate predicted future access times for remaining entries
    for key in metadata:
        meta = metadata[key]
        # For simplicity, we assume predicted future access times remain unchanged in this example