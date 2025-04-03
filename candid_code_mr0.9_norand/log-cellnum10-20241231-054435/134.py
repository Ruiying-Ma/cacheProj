# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
RPA_WEIGHT = 0.4
IFC_WEIGHT = 0.3
DES_WEIGHT = 0.2
QDM_WEIGHT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Recursive Phase Alignment (RPA) scores, Interactive Flux Controller (IFC) states, Dynamic Entropy Synchronizer (DES) values, and Quantum Drift Modulation (QDM) levels for each cache entry. RPA scores track access patterns, IFC states monitor interaction levels, DES values measure data volatility, and QDM levels assess temporal stability.
metadata = defaultdict(lambda: {'RPA': 0, 'IFC': 0, 'DES': 0, 'QDM': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry using a weighted sum of RPA, IFC, DES, and QDM. The entry with the lowest composite score is selected for eviction, prioritizing items with low access frequency, low interaction, high volatility, and low temporal stability.
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
        composite_score = (RPA_WEIGHT * meta['RPA'] +
                           IFC_WEIGHT * meta['IFC'] +
                           DES_WEIGHT * meta['DES'] +
                           QDM_WEIGHT * meta['QDM'])
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the RPA score is incremented to reflect increased access frequency, the IFC state is adjusted to reflect current interaction levels, the DES value is recalibrated to account for reduced volatility, and the QDM level is updated to reflect improved temporal stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['RPA'] += 1
    meta['IFC'] += 1
    meta['DES'] = max(0, meta['DES'] - 1)
    meta['QDM'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the RPA score is initialized to a baseline value, the IFC state is set to a neutral level, the DES value is calculated based on initial data volatility, and the QDM level is set to reflect initial temporal stability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'RPA': 1,
        'IFC': 1,
        'DES': 5,  # Assuming initial volatility
        'QDM': 1
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the overall cache RPA, IFC, DES, and QDM metrics to ensure balanced cache dynamics, adjusting weights and thresholds as necessary to maintain optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove metadata for the evicted object
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]
    
    # Recalibrate weights or thresholds if needed (not implemented here, but could be based on cache dynamics)