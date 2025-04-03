# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QUANTUM_REALIGNMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a set of evolutionary metrics for each cache entry, including access frequency, recency, and a temporal efficiency score that measures the time between accesses. It also tracks causal dynamics by recording the sequence of accesses and a quantum realignment factor that adjusts based on the overall cache state and access patterns.
cache_metadata = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'temporal_efficiency': {},
    'quantum_realignment': defaultdict(lambda: 1.0),
    'causal_dynamics': []
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating a composite score derived from the evolutionary metrics, prioritizing entries with low temporal efficiency and causal impact. The quantum realignment factor is used to break ties, favoring entries that least disrupt the cache's current state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = cache_metadata['access_frequency'][key]
        recency = cache_metadata['recency'].get(key, 0)
        temporal_efficiency = cache_metadata['temporal_efficiency'].get(key, float('inf'))
        quantum_realignment = cache_metadata['quantum_realignment'][key]
        
        # Calculate composite score
        score = (temporal_efficiency * quantum_realignment) / (frequency + 1)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
        elif score == min_score:
            # Break ties using quantum realignment factor
            if quantum_realignment < cache_metadata['quantum_realignment'][candid_obj_key]:
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recency for the entry, recalculates the temporal efficiency score based on the time since the last access, and adjusts the quantum realignment factor to reflect the entry's reinforced importance in the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update access frequency
    cache_metadata['access_frequency'][key] += 1
    
    # Update recency
    last_access_time = cache_metadata['recency'].get(key, current_time)
    cache_metadata['recency'][key] = current_time
    
    # Update temporal efficiency score
    time_since_last_access = current_time - last_access_time
    cache_metadata['temporal_efficiency'][key] = time_since_last_access
    
    # Adjust quantum realignment factor
    cache_metadata['quantum_realignment'][key] *= (1 + QUANTUM_REALIGNMENT_FACTOR)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its evolutionary metrics with default values, sets its causal dynamics based on the current access sequence, and assigns a neutral quantum realignment factor, allowing it to adapt quickly to subsequent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize evolutionary metrics
    cache_metadata['access_frequency'][key] = 1
    cache_metadata['recency'][key] = current_time
    cache_metadata['temporal_efficiency'][key] = float('inf')
    cache_metadata['quantum_realignment'][key] = 1.0
    
    # Update causal dynamics
    cache_metadata['causal_dynamics'].append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the quantum realignment factor for the remaining entries to ensure a balanced cache state, and updates the causal dynamics to reflect the removal, potentially altering the sequence of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove evicted object from metadata
    if evicted_key in cache_metadata['access_frequency']:
        del cache_metadata['access_frequency'][evicted_key]
    if evicted_key in cache_metadata['recency']:
        del cache_metadata['recency'][evicted_key]
    if evicted_key in cache_metadata['temporal_efficiency']:
        del cache_metadata['temporal_efficiency'][evicted_key]
    if evicted_key in cache_metadata['quantum_realignment']:
        del cache_metadata['quantum_realignment'][evicted_key]
    
    # Recalibrate quantum realignment factor for remaining entries
    for key in cache_snapshot.cache:
        cache_metadata['quantum_realignment'][key] *= (1 - QUANTUM_REALIGNMENT_FACTOR)
    
    # Update causal dynamics
    if evicted_key in cache_metadata['causal_dynamics']:
        cache_metadata['causal_dynamics'].remove(evicted_key)