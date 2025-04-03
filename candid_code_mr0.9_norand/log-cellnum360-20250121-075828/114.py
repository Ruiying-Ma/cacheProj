# Import anything you need below
import time

# Put tunable constant parameters below
INITIAL_PREDICTED_INTERVAL = 10  # Initial heuristic assumption for predicted next access time

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted next access time using predictive heuristics, and a dynamic state model that adapts based on observed access patterns.
metadata = {
    'access_frequency': {},  # Dictionary to store access frequency of objects
    'last_access_time': {},  # Dictionary to store last access time of objects
    'predicted_next_access_time': {},  # Dictionary to store predicted next access time of objects
    'dynamic_state_model': {}  # Dictionary to store dynamic state model parameters
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a composite score derived from the least frequently accessed, the longest time since last access, and the predicted next access time. The object with the lowest composite score is evicted.
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
        predicted_next_access = metadata['predicted_next_access_time'].get(key, float('inf'))
        
        # Composite score calculation
        score = (1 / (access_freq + 1)) + (cache_snapshot.access_count - last_access) + predicted_next_access
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, records the current time as the last access time, and recalculates the predicted next access time using a heuristic based on recent access intervals.
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
    
    # Recalculate predicted next access time
    if key in metadata['predicted_next_access_time']:
        last_predicted = metadata['predicted_next_access_time'][key]
        interval = current_time - metadata['last_access_time'].get(key, current_time)
        metadata['predicted_next_access_time'][key] = (last_predicted + interval) / 2
    else:
        metadata['predicted_next_access_time'][key] = INITIAL_PREDICTED_INTERVAL

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the current time as the last access time, and estimates the predicted next access time based on initial heuristic assumptions.
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
    
    # Estimate predicted next access time
    metadata['predicted_next_access_time'][key] = INITIAL_PREDICTED_INTERVAL

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy updates the dynamic state model to refine its predictive heuristics, adjusting parameters to improve future predictions based on the observed access patterns leading to the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for evicted object
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['last_access_time']:
        del metadata['last_access_time'][evicted_key]
    if evicted_key in metadata['predicted_next_access_time']:
        del metadata['predicted_next_access_time'][evicted_key]
    
    # Update dynamic state model (this is a placeholder for more complex logic)
    # For simplicity, we assume the dynamic state model is updated by observing the eviction pattern
    # This can be extended with more sophisticated logic as needed
    metadata['dynamic_state_model'][evicted_key] = {
        'eviction_time': cache_snapshot.access_count,
        'evicted_obj_size': evicted_obj.size
    }