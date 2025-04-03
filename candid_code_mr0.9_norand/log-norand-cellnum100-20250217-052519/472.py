# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
WEIGHT_INVERSE_ACCESS_FREQUENCY = 0.25
WEIGHT_TIME_SINCE_LAST_ACCESS = 0.25
WEIGHT_PREDICTED_FUTURE_ACCESS_TIME = 0.25
WEIGHT_CONTEXTUAL_RELEVANCE_SCORE = 0.25

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access timestamp, predicted future access time, and contextual relevance score based on the current workload and user behavior.
metadata = {
    'access_frequency': {},
    'last_access_timestamp': {},
    'predicted_future_access_time': {},
    'contextual_relevance_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of the inverse of access frequency, the time since last access, the predicted future access time, and the contextual relevance score. The entry with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata['access_frequency'].get(key, 1)
        last_access_timestamp = metadata['last_access_timestamp'].get(key, cache_snapshot.access_count)
        predicted_future_access_time = metadata['predicted_future_access_time'].get(key, cache_snapshot.access_count + 1)
        contextual_relevance_score = metadata['contextual_relevance_score'].get(key, 1)
        
        composite_score = (
            WEIGHT_INVERSE_ACCESS_FREQUENCY / access_frequency +
            WEIGHT_TIME_SINCE_LAST_ACCESS * (cache_snapshot.access_count - last_access_timestamp) +
            WEIGHT_PREDICTED_FUTURE_ACCESS_TIME * predicted_future_access_time +
            WEIGHT_CONTEXTUAL_RELEVANCE_SCORE * contextual_relevance_score
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access timestamp to the current time, recalculates the predicted future access time using the latest access patterns, and adjusts the contextual relevance score based on the current workload and user behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 1  # Simplified prediction
    metadata['contextual_relevance_score'][key] = 1  # Simplified relevance score

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object into the cache, the policy initializes the access frequency to 1, sets the last access timestamp to the current time, predicts the future access time based on initial patterns, and assigns a contextual relevance score based on the current workload and user behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_timestamp'][key] = cache_snapshot.access_count
    metadata['predicted_future_access_time'][key] = cache_snapshot.access_count + 1  # Simplified prediction
    metadata['contextual_relevance_score'][key] = 1  # Simplified relevance score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the contextual relevance scores for the remaining entries to ensure alignment with the current workload and user behavior, and adjusts the predictive coding model to improve future predictions.
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
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['contextual_relevance_score']:
        del metadata['contextual_relevance_score'][evicted_key]
    
    # Recalculate contextual relevance scores for remaining entries
    for key in cache_snapshot.cache.keys():
        metadata['contextual_relevance_score'][key] = 1  # Simplified relevance score