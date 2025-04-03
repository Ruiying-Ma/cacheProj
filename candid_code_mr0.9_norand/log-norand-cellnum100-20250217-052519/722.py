# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
WEIGHT_RECENT_INTERACTION = 0.4
WEIGHT_SESSION_DURATION = 0.3
WEIGHT_ACCESS_FREQUENCY = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including user clickstream data, session duration, interaction frequency, and behavioral patterns such as preferred access times and content types.
metadata = {
    'interaction_time': {},  # Last interaction time for each object
    'session_duration': {},  # Total session duration for each object
    'access_frequency': {},  # Access frequency for each object
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a weighted score derived from the least recent interaction, lowest session duration, and least frequent access patterns, prioritizing objects with the lowest scores.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        interaction_time = metadata['interaction_time'].get(key, 0)
        session_duration = metadata['session_duration'].get(key, 0)
        access_frequency = metadata['access_frequency'].get(key, 0)
        
        score = (WEIGHT_RECENT_INTERACTION * (cache_snapshot.access_count - interaction_time) +
                 WEIGHT_SESSION_DURATION * session_duration +
                 WEIGHT_ACCESS_FREQUENCY * access_frequency)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the interaction frequency, adjusts the session duration, and refines the behavioral pattern analysis for the user associated with the accessed object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update interaction time
    metadata['interaction_time'][key] = current_time
    
    # Update session duration
    if key in metadata['session_duration']:
        metadata['session_duration'][key] += 1
    else:
        metadata['session_duration'][key] = 1
    
    # Update access frequency
    if key in metadata['access_frequency']:
        metadata['access_frequency'][key] += 1
    else:
        metadata['access_frequency'][key] = 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the metadata for the new object with default values and updates the overall clickstream and session data to reflect the new addition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize metadata for the new object
    metadata['interaction_time'][key] = current_time
    metadata['session_duration'][key] = 1
    metadata['access_frequency'][key] = 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes the associated metadata and recalculates the weighted scores for the remaining objects to ensure accurate future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for the evicted object
    if evicted_key in metadata['interaction_time']:
        del metadata['interaction_time'][evicted_key]
    if evicted_key in metadata['session_duration']:
        del metadata['session_duration'][evicted_key]
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    
    # Recalculate weighted scores for remaining objects (if needed)
    # This is implicitly handled in the evict function by recalculating scores on each call