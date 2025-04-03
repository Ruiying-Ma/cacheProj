# Import anything you need below
import time

# Put tunable constant parameters below
PREFETCH_SCORE_INITIAL = 0.5
LATENCY_ESTIMATE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data access latency, and a prefetch prediction score for each cache entry.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'data_access_latency': {},
    'prefetch_prediction_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by iterating through the cache entries in a bounded manner, selecting the entry with the lowest combined score of access frequency, recency, and prefetch prediction score, while considering data access latency to minimize performance impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        last_access = metadata['last_access_time'].get(key, 0)
        prefetch_score = metadata['prefetch_prediction_score'].get(key, PREFETCH_SCORE_INITIAL)
        latency = metadata['data_access_latency'].get(key, LATENCY_ESTIMATE)
        
        combined_score = access_freq + (cache_snapshot.access_count - last_access) + prefetch_score + latency
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and adjusts the prefetch prediction score based on the observed access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['prefetch_prediction_score'][key] = adjust_prefetch_score(metadata['prefetch_prediction_score'].get(key, PREFETCH_SCORE_INITIAL))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, estimates the data access latency, and assigns an initial prefetch prediction score based on historical data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['data_access_latency'][key] = LATENCY_ESTIMATE
    metadata['prefetch_prediction_score'][key] = PREFETCH_SCORE_INITIAL

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted entry and recalculates the prefetch prediction scores for the remaining entries to adapt to the new cache state.
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
    if evicted_key in metadata['data_access_latency']:
        del metadata['data_access_latency'][evicted_key]
    if evicted_key in metadata['prefetch_prediction_score']:
        del metadata['prefetch_prediction_score'][evicted_key]
    
    # Recalculate prefetch prediction scores for remaining entries
    for key in cache_snapshot.cache:
        metadata['prefetch_prediction_score'][key] = adjust_prefetch_score(metadata['prefetch_prediction_score'].get(key, PREFETCH_SCORE_INITIAL))

def adjust_prefetch_score(current_score):
    '''
    Adjust the prefetch prediction score based on the observed access pattern.
    This is a placeholder function and should be implemented based on specific requirements.
    - Args:
        - `current_score`: The current prefetch prediction score.
    - Return:
        - `new_score`: The adjusted prefetch prediction score.
    '''
    # Placeholder logic for adjusting prefetch score
    new_score = current_score * 0.9
    return new_score