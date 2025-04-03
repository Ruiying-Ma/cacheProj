# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 1
PHI_INCREMENT = 1
ETA_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains an Adaptive Quantum Matrix (AQM) that records access frequencies and recency for each cache entry, a Dynamic Spectrum Analysis (DSA) score that reflects the variability of access patterns, a Predictive Harmony Index (PHI) that forecasts future access likelihood, and an Entropic Threshold Adjustment (ETA) value that dynamically adjusts the sensitivity of eviction decisions.
AQM = defaultdict(lambda: {'frequency': 0, 'recency': 0})
DSA_score = 0
PHI = defaultdict(lambda: 0)
ETA = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying entries with the lowest PHI, adjusted by the current ETA. If multiple candidates exist, it selects the one with the least recent access according to the AQM.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_phi = float('inf')
    min_recency = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_phi = PHI[key] * ETA
        if adjusted_phi < min_phi or (adjusted_phi == min_phi and AQM[key]['recency'] < min_recency):
            min_phi = adjusted_phi
            min_recency = AQM[key]['recency']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the AQM is updated to increase the recency and frequency of the accessed entry, the DSA score is recalculated to reflect the current access pattern, and the PHI is adjusted upwards to indicate a higher likelihood of future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    AQM[key]['frequency'] += 1
    AQM[key]['recency'] = cache_snapshot.access_count
    PHI[key] += PHI_INCREMENT
    # Recalculate DSA score (simplified as a sum of frequencies for this example)
    global DSA_score
    DSA_score = sum(AQM[k]['frequency'] for k in cache_snapshot.cache)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the AQM initializes the entry with a baseline frequency and recency, the DSA score is updated to account for the new entry's impact on access patterns, and the PHI is set based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    AQM[key] = {'frequency': BASELINE_FREQUENCY, 'recency': cache_snapshot.access_count}
    PHI[key] = BASELINE_FREQUENCY
    # Update DSA score
    global DSA_score
    DSA_score = sum(AQM[k]['frequency'] for k in cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the AQM removes the evicted entry, the DSA score is recalibrated to reflect the reduced cache diversity, and the ETA is adjusted to fine-tune future eviction sensitivity based on the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in AQM:
        del AQM[evicted_key]
    if evicted_key in PHI:
        del PHI[evicted_key]
    # Recalculate DSA score
    global DSA_score
    DSA_score = sum(AQM[k]['frequency'] for k in cache_snapshot.cache)
    # Adjust ETA
    global ETA
    ETA = max(0.1, ETA - ETA_ADJUSTMENT_FACTOR)