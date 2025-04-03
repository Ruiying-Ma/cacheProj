# Import anything you need below
import math

# Put tunable constant parameters below
INITIAL_TFS = 1.0
INITIAL_AEI = 1.0
DPSI_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Quantum Loop Counters (QLC) for each cache entry, Temporal Frequency Scores (TFS), an Adaptive Entropy Index (AEI), and a Dynamic Phase Shift Indicator (DPSI) to track the phase of access patterns.
metadata = {
    'QLC': {},  # Quantum Loop Counters for each cache entry
    'TFS': {},  # Temporal Frequency Scores for each cache entry
    'AEI': {},  # Adaptive Entropy Index for each cache entry
    'DPSI': 0.0  # Dynamic Phase Shift Indicator
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score of TFS and AEI, adjusted by the DPSI. This ensures that entries with low temporal frequency and high entropy are prioritized for eviction, while considering the current access phase.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        tfs = metadata['TFS'].get(key, INITIAL_TFS)
        aei = metadata['AEI'].get(key, INITIAL_AEI)
        score = tfs + aei - metadata['DPSI']
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QLC for the accessed entry is incremented, the TFS is recalibrated based on recent access patterns, and the AEI is adjusted to reflect reduced uncertainty. The DPSI is updated to reflect any phase shift detected in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['QLC'][key] = metadata['QLC'].get(key, 0) + 1
    metadata['TFS'][key] = metadata['QLC'][key] / cache_snapshot.access_count
    metadata['AEI'][key] = max(0, metadata['AEI'].get(key, INITIAL_AEI) - 0.1)
    metadata['DPSI'] += DPSI_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QLC is initialized, the TFS is set based on initial access frequency predictions, the AEI is calculated to reflect initial uncertainty, and the DPSI is adjusted to account for the potential impact of the new entry on access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['QLC'][key] = 0
    metadata['TFS'][key] = INITIAL_TFS
    metadata['AEI'][key] = INITIAL_AEI
    metadata['DPSI'] -= DPSI_ADJUSTMENT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QLC of the evicted entry is reset, the TFS of remaining entries is recalibrated to reflect the new cache state, the AEI is adjusted to account for reduced entropy, and the DPSI is updated to reflect any phase shift resulting from the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['QLC']:
        del metadata['QLC'][evicted_key]
    if evicted_key in metadata['TFS']:
        del metadata['TFS'][evicted_key]
    if evicted_key in metadata['AEI']:
        del metadata['AEI'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['TFS'][key] = metadata['QLC'].get(key, 0) / cache_snapshot.access_count
        metadata['AEI'][key] = max(0, metadata['AEI'].get(key, INITIAL_AEI) - 0.1)
    
    metadata['DPSI'] -= DPSI_ADJUSTMENT_FACTOR