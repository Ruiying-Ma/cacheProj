# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_EBS = 1.0
EBS_INCREMENT = 0.5
THV_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains an Entropic Balance Score (EBS) for each cache entry, a Quantum Loopback Counter (QLC), a Temporal Heuristic Value (THV), and a Predictive Matrix (PM) that forecasts future access patterns based on historical data.
metadata = {
    'EBS': defaultdict(lambda: INITIAL_EBS),
    'QLC': defaultdict(int),
    'THV': defaultdict(int),
    'PM': defaultdict(list)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest Entropic Balance Score, adjusted by the Quantum Loopback Counter and Temporal Heuristic Value, while consulting the Predictive Matrix to ensure minimal future impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        ebs = metadata['EBS'][key]
        qlc = metadata['QLC'][key]
        thv = metadata['THV'][key]
        score = ebs - qlc + thv
        
        # Consult Predictive Matrix to ensure minimal future impact
        if key in metadata['PM'] and obj.key in metadata['PM'][key]:
            score += 1  # Increase score if future access is predicted
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Entropic Balance Score is increased to reflect the entry's relevance, the Quantum Loopback Counter is reset to zero, the Temporal Heuristic Value is updated based on the time since the last access, and the Predictive Matrix is refined to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['EBS'][key] += EBS_INCREMENT
    metadata['QLC'][key] = 0
    metadata['THV'][key] = cache_snapshot.access_count - metadata['THV'][key]
    
    # Update Predictive Matrix
    for other_key in cache_snapshot.cache:
        if other_key != key:
            metadata['PM'][other_key].append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Entropic Balance Score is initialized to a neutral value, the Quantum Loopback Counter is set to zero, the Temporal Heuristic Value is calculated based on the current time, and the Predictive Matrix is updated to include the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['EBS'][key] = INITIAL_EBS
    metadata['QLC'][key] = 0
    metadata['THV'][key] = cache_snapshot.access_count
    
    # Update Predictive Matrix
    for other_key in cache_snapshot.cache:
        if other_key != key:
            metadata['PM'][other_key].append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Entropic Balance Scores of remaining entries are adjusted to reflect the new cache state, the Quantum Loopback Counters are incremented, the Temporal Heuristic Values are recalibrated, and the Predictive Matrix is updated to remove the evicted entry's influence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    for key in cache_snapshot.cache:
        metadata['EBS'][key] *= THV_DECAY_FACTOR
        metadata['QLC'][key] += 1
        metadata['THV'][key] = cache_snapshot.access_count - metadata['THV'][key]
        
        # Update Predictive Matrix
        if evicted_key in metadata['PM'][key]:
            metadata['PM'][key].remove(evicted_key)