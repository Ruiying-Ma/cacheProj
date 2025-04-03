# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for LFU
BETA = 0.5   # Weight for LRU

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, context tags (e.g., user behavior, application type), and a dynamic load prediction score derived from quantum signal processing techniques.
metadata = {
    'access_frequency': {},  # key -> frequency
    'last_access_time': {},  # key -> last access time
    'context_tags': {},      # key -> context tags
    'load_prediction_score': {}  # key -> load prediction score
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining the least frequently used (LFU) and least recently used (LRU) strategies, adjusted by the context tags and dynamic load prediction score to ensure scalability and context-aware adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        load_score = metadata['load_prediction_score'].get(key, 0)
        
        combined_score = ALPHA * freq + BETA * (cache_snapshot.access_count - last_access) + load_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the last access time is updated, and the context tags are re-evaluated. The dynamic load prediction score is recalculated using quantum signal processing to reflect the current load and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['context_tags'][key] = evaluate_context_tags(obj)
    metadata['load_prediction_score'][key] = calculate_load_prediction_score(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the last access time to the current time, assigns context tags based on the insertion context, and computes an initial dynamic load prediction score using quantum signal processing.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['context_tags'][key] = evaluate_context_tags(obj)
    metadata['load_prediction_score'][key] = calculate_load_prediction_score(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy rebalances the remaining metadata by adjusting the access frequencies, updating the last access times, and recalculating the dynamic load prediction scores to reflect the new cache state and ensure optimal performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['context_tags']:
        del metadata['context_tags'][evicted_key]
    if evicted_key in metadata['load_prediction_score']:
        del metadata['load_prediction_score'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0)
        metadata['last_access_time'][key] = metadata['last_access_time'].get(key, cache_snapshot.access_count)
        metadata['load_prediction_score'][key] = calculate_load_prediction_score(cache_snapshot.cache[key])

def evaluate_context_tags(obj):
    # Dummy function to evaluate context tags based on the object
    return "default"

def calculate_load_prediction_score(obj):
    # Dummy function to calculate load prediction score using quantum signal processing
    return math.log(obj.size + 1)