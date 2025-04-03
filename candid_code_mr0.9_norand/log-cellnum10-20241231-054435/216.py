# Import anything you need below
import time

# Put tunable constant parameters below
BASELINE_QRI = 1
INITIAL_DPS = 1
NEUTRAL_ETC = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Resonance Index (QRI) for each cache entry, a Dynamic Phase Shift (DPS) value to track access patterns, an Entropic Threshold Calibration (ETC) to measure cache entry stability, and a Temporal Precision Mapping (TPM) to record precise access timestamps.
metadata = {
    'QRI': {},  # Quantum Resonance Index
    'DPS': {},  # Dynamic Phase Shift
    'ETC': {},  # Entropic Threshold Calibration
    'TPM': {}   # Temporal Precision Mapping
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest QRI, adjusted by the DPS to account for recent access patterns, and further filtered by the ETC to ensure stability. The entry with the lowest combined score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        qri = metadata['QRI'].get(key, BASELINE_QRI)
        dps = metadata['DPS'].get(key, INITIAL_DPS)
        etc = metadata['ETC'].get(key, NEUTRAL_ETC)
        score = qri - dps + etc
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QRI of the accessed entry is incremented to reflect its increased resonance, the DPS is adjusted to reflect the current access phase, the ETC is recalibrated to account for the entry's stability, and the TPM is updated with the current timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['QRI'][key] = metadata['QRI'].get(key, BASELINE_QRI) + 1
    metadata['DPS'][key] = metadata['DPS'].get(key, INITIAL_DPS) + 1
    metadata['ETC'][key] = metadata['ETC'].get(key, NEUTRAL_ETC) + 1
    metadata['TPM'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QRI is initialized to a baseline value, the DPS is set to reflect the initial phase of access, the ETC is calibrated to a neutral stability level, and the TPM is set to the current timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['QRI'][key] = BASELINE_QRI
    metadata['DPS'][key] = INITIAL_DPS
    metadata['ETC'][key] = NEUTRAL_ETC
    metadata['TPM'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the ETC of remaining entries to reflect the new cache dynamics, adjusts the DPS to account for the change in access patterns, and updates the TPM to ensure temporal accuracy across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in metadata['QRI']:
        del metadata['QRI'][evicted_key]
    if evicted_key in metadata['DPS']:
        del metadata['DPS'][evicted_key]
    if evicted_key in metadata['ETC']:
        del metadata['ETC'][evicted_key]
    if evicted_key in metadata['TPM']:
        del metadata['TPM'][evicted_key]

    for key in cache_snapshot.cache:
        metadata['ETC'][key] = metadata['ETC'].get(key, NEUTRAL_ETC) + 1
        metadata['DPS'][key] = metadata['DPS'].get(key, INITIAL_DPS) + 1
        metadata['TPM'][key] = cache_snapshot.access_count