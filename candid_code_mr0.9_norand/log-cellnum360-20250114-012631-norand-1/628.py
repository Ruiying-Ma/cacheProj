# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for predicted future access time
BETA = 0.3   # Weight for current load
GAMMA = 0.2  # Weight for temporal data convergence

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time using neural phase modulation, and context tags derived from context-aware synthesis.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'predicted_future_access_time': {},
    'context_tags': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a composite score that balances predicted future access time, current load, and temporal data convergence. The item with the lowest score is evicted.
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
        predicted_future_access = metadata['predicted_future_access_time'].get(key, float('inf'))
        
        current_time = cache_snapshot.access_count
        temporal_data_convergence = current_time - last_access
        
        score = (ALPHA * predicted_future_access) + (BETA * cached_obj.size) + (GAMMA * temporal_data_convergence)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency, last access time, and refines the predicted future access time using neural phase modulation. Context tags are also updated based on the current context.
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
    
    # Refine predicted future access time using neural phase modulation (simplified as exponential decay)
    metadata['predicted_future_access_time'][key] = current_time + math.exp(-metadata['access_frequency'][key])
    
    # Update context tags (simplified as a placeholder)
    metadata['context_tags'][key] = 'updated_context'

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency, sets the last access time to the current time, predicts the future access time using neural phase modulation, and assigns initial context tags.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize access frequency
    metadata['access_frequency'][key] = 1
    
    # Set last access time to current time
    metadata['last_access_time'][key] = current_time
    
    # Predict future access time using neural phase modulation (simplified as exponential decay)
    metadata['predicted_future_access_time'][key] = current_time + math.exp(-metadata['access_frequency'][key])
    
    # Assign initial context tags (simplified as a placeholder)
    metadata['context_tags'][key] = 'initial_context'

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the load balance and adjusts the temporal data convergence parameters to optimize future eviction decisions. Context tags are also re-evaluated to ensure relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata of the evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_future_access_time']:
        del metadata['predicted_future_access_time'][evicted_key]
    if evicted_key in metadata['context_tags']:
        del metadata['context_tags'][evicted_key]
    
    # Recalculate load balance and adjust temporal data convergence parameters (simplified as placeholders)
    # This part can be expanded based on specific requirements and available data
    # For now, we assume the recalculations are done implicitly by the nature of the cache operations