# Import anything you need below
import time

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 1.0
WEIGHT_LAST_ACCESS_TIME = 1.0
WEIGHT_DATA_SIZE = 1.0
WEIGHT_COHERENCY_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data size, and a coherency score that indicates the importance of maintaining coherency for each cache line.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'data_size': {},
    'coherency_score': {}
}

def calculate_coherency_score(obj):
    # Placeholder for coherency score calculation based on data dependencies
    return 1.0

def calculate_eviction_score(key):
    return (WEIGHT_ACCESS_FREQUENCY * metadata['access_frequency'][key] +
            WEIGHT_LAST_ACCESS_TIME * (time.time() - metadata['last_access_time'][key]) +
            WEIGHT_DATA_SIZE * metadata['data_size'][key] +
            WEIGHT_COHERENCY_SCORE * metadata['coherency_score'][key])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score that combines low access frequency, old last access time, large data size, and low coherency score. The cache line with the lowest combined score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_eviction_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the access frequency, updates the last access time to the current time, and recalculates the coherency score based on recent access patterns and data dependencies.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = time.time()
    metadata['coherency_score'][key] = calculate_coherency_score(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, calculates the initial coherency score based on the object's data dependencies, and records the data size.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = time.time()
    metadata['data_size'][key] = obj.size
    metadata['coherency_score'][key] = calculate_coherency_score(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all metadata associated with the evicted cache line and adjusts the coherency scores of remaining cache lines if they were dependent on the evicted data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['data_size'][evicted_key]
    del metadata['coherency_score'][evicted_key]
    
    # Adjust coherency scores of remaining cache lines if they were dependent on the evicted data
    for key in cache_snapshot.cache:
        metadata['coherency_score'][key] = calculate_coherency_score(cache_snapshot.cache[key])