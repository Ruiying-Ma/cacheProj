# Import anything you need below
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIMESTAMP = 1.0
WEIGHT_DATA_INTEGRATION_SCORE = 1.0
WEIGHT_MEMORY_FOOTPRINT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including access frequency, last access timestamp, data integration score, and memory footprint.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that combines low access frequency, old last access timestamp, low data integration score, and high memory footprint.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata[key]['access_frequency']
        last_access_timestamp = metadata[key]['last_access_timestamp']
        data_integration_score = metadata[key]['data_integration_score']
        memory_footprint = metadata[key]['memory_footprint']
        
        score = (WEIGHT_ACCESS_FREQUENCY / access_frequency +
                 WEIGHT_LAST_ACCESS_TIMESTAMP * (cache_snapshot.access_count - last_access_timestamp) +
                 WEIGHT_DATA_INTEGRATION_SCORE / data_integration_score +
                 WEIGHT_MEMORY_FOOTPRINT * memory_footprint)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the access frequency, updates the last access timestamp to the current time, and recalculates the data integration score based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['access_frequency'] += 1
    metadata[key]['last_access_timestamp'] = cache_snapshot.access_count
    metadata[key]['data_integration_score'] = calculate_data_integration_score(metadata[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, calculates an initial data integration score, and records the memory footprint of the object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'access_frequency': 1,
        'last_access_timestamp': cache_snapshot.access_count,
        'data_integration_score': calculate_data_integration_score({'access_frequency': 1}),
        'memory_footprint': obj.size
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all metadata associated with the evicted object and recalculates the data integration scores for the remaining objects to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata[evicted_key]
    
    for key in metadata:
        metadata[key]['data_integration_score'] = calculate_data_integration_score(metadata[key])

def calculate_data_integration_score(meta):
    '''
    This function calculates the data integration score based on the metadata.
    - Args:
        - `meta`: The metadata of the object.
    - Return:
        - `score`: The calculated data integration score.
    '''
    # Example calculation, can be adjusted based on specific needs
    return meta['access_frequency'] * 1.0