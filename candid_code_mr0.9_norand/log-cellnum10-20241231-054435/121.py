# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 1
NEUTRAL_EPC = 0.5
INITIAL_NSP = 0.5
MAX_TFI = 1.0
TFI_DECAY_RATE = 0.01

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Matrix Dynamic (QMD) that records access frequencies and recency in a multi-dimensional matrix. It also tracks Entropic Phase Calibration (EPC) values to measure the randomness of access patterns, Neural Synchronization Protocol (NSP) scores to predict future accesses, and Temporal Flux Integration (TFI) to account for time-based decay of data relevance.
QMD = defaultdict(lambda: {'frequency': BASELINE_FREQUENCY, 'recency': BASELINE_RECENCY})
EPC = defaultdict(lambda: NEUTRAL_EPC)
NSP = defaultdict(lambda: INITIAL_NSP)
TFI = defaultdict(lambda: MAX_TFI)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score from the QMD, EPC, and NSP, adjusted by the TFI. This ensures that items with low access frequency, high randomness, low future access prediction, and diminished temporal relevance are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        qmd_score = QMD[key]['frequency'] + QMD[key]['recency']
        epc_score = EPC[key]
        nsp_score = NSP[key]
        tfi_score = TFI[key]
        
        combined_score = qmd_score - epc_score + nsp_score - tfi_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QMD is updated to increase the frequency and recency scores for the accessed item. The EPC is recalibrated to reflect reduced randomness, the NSP score is adjusted upwards to indicate a higher likelihood of future access, and the TFI is reset to reflect renewed temporal relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QMD[key]['frequency'] += 1
    QMD[key]['recency'] = cache_snapshot.access_count
    EPC[key] *= 0.9  # Reduce randomness
    NSP[key] += 0.1  # Increase future access prediction
    TFI[key] = MAX_TFI  # Reset temporal relevance

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QMD initializes frequency and recency scores to baseline values. The EPC is set to a neutral state, the NSP score is initialized based on initial access predictions, and the TFI is set to maximum temporal relevance to reflect the freshness of the data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QMD[key] = {'frequency': BASELINE_FREQUENCY, 'recency': cache_snapshot.access_count}
    EPC[key] = NEUTRAL_EPC
    NSP[key] = INITIAL_NSP
    TFI[key] = MAX_TFI

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QMD is adjusted to remove the evicted item's scores, the EPC is recalibrated to account for the change in access pattern entropy, the NSP is updated to reflect the removal's impact on future predictions, and the TFI is recalibrated to maintain overall temporal balance in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del QMD[evicted_key]
    del EPC[evicted_key]
    del NSP[evicted_key]
    del TFI[evicted_key]
    
    # Recalibrate EPC and NSP for remaining items
    for key in cache_snapshot.cache:
        EPC[key] *= 1.1  # Slightly increase randomness
        NSP[key] *= 0.9  # Slightly decrease future access prediction
    
    # Decay TFI for all items
    for key in TFI:
        TFI[key] = max(0, TFI[key] - TFI_DECAY_RATE)