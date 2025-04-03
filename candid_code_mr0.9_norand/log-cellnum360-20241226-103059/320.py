# Import anything you need below
import math

# Put tunable constant parameters below
BASE_ENP_SCORE = 1.0
NEUTRAL_PSS_VALUE = 0.5
ACI_ADJUSTMENT_FACTOR = 0.1
ENP_ADJUSTMENT_FACTOR = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Resonance Curve (QRC) for each cache entry, an Entropic Neural Pathway (ENP) score, a Predictive Symmetry Shift (PSS) value, and an Adaptive Convergence Index (ACI) for the entire cache. The QRC represents the temporal access pattern, the ENP score indicates the complexity of access patterns, the PSS value predicts future access likelihood, and the ACI measures overall cache stability.
metadata = {
    'QRC': {},  # {key: last_access_time}
    'ENP': {},  # {key: enp_score}
    'PSS': {},  # {key: pss_value}
    'ACI': 0.0  # overall cache stability
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of QRC and PSS, adjusted by the ENP score. This ensures that entries with less predictable and less frequent access patterns are evicted first, while considering the overall cache stability through the ACI.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        qrc = metadata['QRC'].get(key, 0)
        enp = metadata['ENP'].get(key, BASE_ENP_SCORE)
        pss = metadata['PSS'].get(key, NEUTRAL_PSS_VALUE)
        
        score = (qrc + pss) / enp
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QRC of the accessed entry is updated to reflect the new access time, the ENP score is recalculated to account for the change in access pattern complexity, and the PSS value is adjusted to increase the likelihood of future access. The ACI is updated to reflect the increased stability of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update QRC
    metadata['QRC'][key] = current_time
    
    # Recalculate ENP
    metadata['ENP'][key] = metadata['ENP'].get(key, BASE_ENP_SCORE) + ENP_ADJUSTMENT_FACTOR
    
    # Adjust PSS
    metadata['PSS'][key] = metadata['PSS'].get(key, NEUTRAL_PSS_VALUE) + 0.1
    
    # Update ACI
    metadata['ACI'] += ACI_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QRC is initialized based on the current time, the ENP score is set to a baseline value indicating minimal complexity, the PSS value is initialized to a neutral prediction, and the ACI is recalculated to incorporate the new entry's impact on cache stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize QRC
    metadata['QRC'][key] = current_time
    
    # Set ENP to baseline
    metadata['ENP'][key] = BASE_ENP_SCORE
    
    # Initialize PSS
    metadata['PSS'][key] = NEUTRAL_PSS_VALUE
    
    # Recalculate ACI
    metadata['ACI'] += ACI_ADJUSTMENT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the ACI is recalculated to reflect the change in cache composition, ensuring that the overall stability and adaptability of the cache are maintained. The metadata of the evicted entry is discarded, and the remaining entries' ENP scores are slightly adjusted to account for the reduced complexity in the cache environment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Discard metadata of evicted entry
    metadata['QRC'].pop(evicted_key, None)
    metadata['ENP'].pop(evicted_key, None)
    metadata['PSS'].pop(evicted_key, None)
    
    # Recalculate ACI
    metadata['ACI'] -= ACI_ADJUSTMENT_FACTOR
    
    # Adjust remaining ENP scores
    for key in metadata['ENP']:
        metadata['ENP'][key] -= ENP_ADJUSTMENT_FACTOR