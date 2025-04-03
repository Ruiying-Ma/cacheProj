# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
INITIAL_QUANTUM_STATE = 0.5
HEURISTIC_DECAY = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, predicted future access time, and a quantum state value representing the cache line's stability. It also keeps a heuristic score for each cache line based on adaptive learning from past eviction decisions.
metadata = {
    'access_frequency': {},
    'last_access_time': {},
    'quantum_state': {},
    'heuristic_score': {}
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining the least frequently accessed data, the longest time since last access, and the least stable quantum state. It also considers the heuristic score to predict the least likely needed cache line in the near future.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (
            metadata['access_frequency'][key] * 0.2 +
            (cache_snapshot.access_count - metadata['last_access_time'][key]) * 0.3 +
            metadata['quantum_state'][key] * 0.2 +
            metadata['heuristic_score'][key] * 0.3
        )
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency by incrementing it, records the current time as the last access time, recalibrates the quantum state to reflect increased stability, and adjusts the heuristic score based on the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['quantum_state'][key] = min(1.0, metadata['quantum_state'][key] + 0.1)
    metadata['heuristic_score'][key] *= HEURISTIC_DECAY

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency to 1, sets the last access time to the current time, assigns an initial quantum state value indicating moderate stability, and calculates an initial heuristic score based on the object's predicted future access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['quantum_state'][key] = INITIAL_QUANTUM_STATE
    metadata['heuristic_score'][key] = 1.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes all associated metadata for the evicted cache line, recalibrates the quantum states of remaining cache lines to reflect the new cache environment, and updates the heuristic solver to improve future eviction decisions based on the outcome.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['last_access_time'][evicted_key]
    del metadata['quantum_state'][evicted_key]
    del metadata['heuristic_score'][evicted_key]
    
    for key in metadata['quantum_state']:
        metadata['quantum_state'][key] = max(0.0, metadata['quantum_state'][key] - 0.1)