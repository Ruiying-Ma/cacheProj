# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QFS_WEIGHT = 0.4
HCI_WEIGHT = 0.3
TFV_WEIGHT = 0.2
EL_WEIGHT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Quantum Feedback Score (QFS), Heuristic Calibration Index (HCI), Temporal Flux Value (TFV), and Entropy Level (EL) for each cache entry. QFS measures the quantum state of access frequency, HCI adjusts based on heuristic patterns, TFV tracks time-based access changes, and EL measures randomness in access patterns.
metadata = defaultdict(lambda: {'QFS': 0, 'HCI': 0, 'TFV': 0, 'EL': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry using a weighted sum of QFS, HCI, TFV, and EL. The entry with the lowest composite score is selected for eviction, prioritizing those with low access frequency, poor heuristic alignment, outdated temporal relevance, and high entropy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        composite_score = (QFS_WEIGHT * meta['QFS'] +
                           HCI_WEIGHT * meta['HCI'] +
                           TFV_WEIGHT * meta['TFV'] +
                           EL_WEIGHT * meta['EL'])
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QFS is incremented to reflect increased access frequency, HCI is recalibrated based on recent access patterns, TFV is adjusted to account for the current time flux, and EL is recalculated to reflect reduced randomness.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['QFS'] += 1
    meta['HCI'] = (meta['HCI'] + 1) / 2  # Example heuristic recalibration
    meta['TFV'] = cache_snapshot.access_count - meta['TFV']
    meta['EL'] = max(0, meta['EL'] - 0.1)  # Reduce entropy

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, QFS is initialized to a baseline value, HCI is set based on initial heuristic predictions, TFV is initialized to reflect the current time, and EL is set to a neutral value indicating unknown randomness.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'QFS': 1,
        'HCI': 0.5,  # Initial heuristic prediction
        'TFV': cache_snapshot.access_count,
        'EL': 0.5  # Neutral entropy
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates HCI across remaining entries to adjust for the changed cache landscape, TFV is updated to reflect the new temporal state, and EL is recalculated to account for the reduced entropy in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['HCI'] = (meta['HCI'] + 0.5) / 2  # Recalibrate HCI
        meta['TFV'] = cache_snapshot.access_count - meta['TFV']
        meta['EL'] = max(0, meta['EL'] - 0.1)  # Reduce entropy