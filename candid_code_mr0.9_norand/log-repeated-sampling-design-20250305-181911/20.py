# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
DEFAULT_WARM_VALUE = 10
SIGNIFICANT_INCREASE = 5
MINOR_INCREASE = 1
MINOR_DECREASE = 1

# Put the metadata specifically maintained by the policy below. Maintains a heatmap of cache blocks based on access frequency over time, where each block has a temperature score increasing with more frequent access and decreasing over time intervals without access.
temperature_scores = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    Chooses the eviction victim based on the lowest temperature score among the cache blocks, preferring colder blocks that are accessed less frequently and fewer times recently.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_temp_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        if temperature_scores[key] < min_temp_score:
            min_temp_score = temperature_scores[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Increases the temperature score of the accessed cache block significantly, representing a recent access, and applies a minor increase to adjacent blocks to simulate spatial locality.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temperature_scores[key] += SIGNIFICANT_INCREASE
    
    # Apply minor increase to adjacent blocks
    keys = list(cache_snapshot.cache.keys())
    idx = keys.index(key)
    if idx > 0:
        temperature_scores[keys[idx - 1]] += MINOR_INCREASE
    if idx < len(keys) - 1:
        temperature_scores[keys[idx + 1]] += MINOR_INCREASE

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Initializes the new object's temperature score based on a default warm value and increases adjacent blocks' scores slightly to account for temporal and spatial locality.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temperature_scores[key] = DEFAULT_WARM_VALUE
    
    # Apply minor increase to adjacent blocks
    keys = list(cache_snapshot.cache.keys())
    idx = keys.index(key)
    if idx > 0:
        temperature_scores[keys[idx - 1]] += MINOR_INCREASE
    if idx < len(keys) - 1:
        temperature_scores[keys[idx + 1]] += MINOR_INCREASE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Removes the temperature score of the evicted block completely and slightly decreases the score of adjacent blocks to reflect the removed block from the cache space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del temperature_scores[evicted_key]
    
    # Apply minor decrease to adjacent blocks
    keys = list(cache_snapshot.cache.keys())
    if evicted_key in keys:
        idx = keys.index(evicted_key)
        if idx > 0:
            temperature_scores[keys[idx - 1]] -= MINOR_DECREASE
        if idx < len(keys) - 1:
            temperature_scores[keys[idx + 1]] -= MINOR_DECREASE