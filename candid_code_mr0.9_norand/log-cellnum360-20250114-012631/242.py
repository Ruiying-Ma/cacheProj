# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_ERROR_PREDICTION_SCORE = 0.5
INITIAL_TEMPORAL_COHERENCE_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, error prediction scores, and temporal coherence scores for each cache entry.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'error_prediction_score': {},
    'temporal_coherence_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which combines low access frequency, high error prediction score, and low temporal coherence. The entry with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        access_freq = metadata['access_frequency'].get(key, 0)
        error_pred_score = metadata['error_prediction_score'].get(key, INITIAL_ERROR_PREDICTION_SCORE)
        temporal_coherence = metadata['temporal_coherence_score'].get(key, INITIAL_TEMPORAL_COHERENCE_SCORE)
        
        composite_score = (1 / (access_freq + 1)) + error_pred_score + (1 / (temporal_coherence + 1))
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, recalculates the error prediction score based on recent access patterns, and updates the temporal coherence score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access frequency
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    
    # Update last access time
    metadata['last_access_time'][key] = current_time
    
    # Recalculate error prediction score (dummy implementation)
    metadata['error_prediction_score'][key] = 1 / (metadata['access_frequency'][key] + 1)
    
    # Update temporal coherence score (dummy implementation)
    metadata['temporal_coherence_score'][key] = 1 / (current_time - metadata['last_access_time'].get(key, current_time) + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, assigns an initial error prediction score based on historical data, and calculates an initial temporal coherence score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize access frequency
    metadata['access_frequency'][key] = 1
    
    # Set last access time
    metadata['last_access_time'][key] = current_time
    
    # Assign initial error prediction score
    metadata['error_prediction_score'][key] = INITIAL_ERROR_PREDICTION_SCORE
    
    # Calculate initial temporal coherence score
    metadata['temporal_coherence_score'][key] = INITIAL_TEMPORAL_COHERENCE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted entry and recalibrates the error prediction model and temporal coherence metrics for the remaining entries to ensure accuracy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove all associated metadata for the evicted entry
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['error_prediction_score']:
        del metadata['error_prediction_score'][evicted_key]
    if evicted_key in metadata['temporal_coherence_score']:
        del metadata['temporal_coherence_score'][evicted_key]
    
    # Recalibrate error prediction model and temporal coherence metrics for remaining entries (dummy implementation)
    for key in cache_snapshot.cache:
        metadata['error_prediction_score'][key] = 1 / (metadata['access_frequency'][key] + 1)
        metadata['temporal_coherence_score'][key] = 1 / (cache_snapshot.access_count - metadata['last_access_time'][key] + 1)