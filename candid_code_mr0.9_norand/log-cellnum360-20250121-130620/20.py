# Import anything you need below
import math

# Put tunable constant parameters below
LEARNING_RATE = 0.01
INITIAL_ENTROPY = 1.0
INITIAL_HEURISTIC_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including entanglement entropy values for each cache entry, a heuristic score based on access patterns, a dynamic adjustment factor influenced by nonlinear dynamics, and a learning rate for adaptive adjustments.
metadata = {
    'entropy': {},  # Entanglement entropy values for each cache entry
    'heuristic': {},  # Heuristic score based on access patterns
    'dynamic_factor': 1.0  # Dynamic adjustment factor
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the highest entanglement entropy value, adjusted by the heuristic score and the dynamic adjustment factor, ensuring a balance between frequently and infrequently accessed items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = -math.inf
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (metadata['entropy'][key] + metadata['heuristic'][key]) * metadata['dynamic_factor']
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the entanglement entropy value of the accessed entry is decreased slightly, the heuristic score is increased based on recent access patterns, and the dynamic adjustment factor is recalibrated using the learning rate to reflect the new state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['entropy'][key] = max(0, metadata['entropy'][key] - LEARNING_RATE)
    metadata['heuristic'][key] += LEARNING_RATE
    metadata['dynamic_factor'] *= (1 + LEARNING_RATE)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its entanglement entropy value, sets an initial heuristic score based on predicted access patterns, and adjusts the dynamic adjustment factor to account for the new entry, with the learning rate guiding the magnitude of these changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['entropy'][key] = INITIAL_ENTROPY
    metadata['heuristic'][key] = INITIAL_HEURISTIC_SCORE
    metadata['dynamic_factor'] *= (1 + LEARNING_RATE)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the entanglement entropy values for the remaining entries, updates the heuristic scores to reflect the new cache composition, and adjusts the dynamic adjustment factor to maintain optimal cache performance, guided by the learning rate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['entropy']:
        del metadata['entropy'][evicted_key]
    if evicted_key in metadata['heuristic']:
        del metadata['heuristic'][evicted_key]
    
    for key in cache_snapshot.cache.keys():
        metadata['entropy'][key] *= (1 - LEARNING_RATE)
        metadata['heuristic'][key] *= (1 + LEARNING_RATE)
    
    metadata['dynamic_factor'] *= (1 - LEARNING_RATE)