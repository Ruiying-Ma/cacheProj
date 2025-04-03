# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TSI = 5
BASELINE_DFM = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Transition Matrix (QTM) to track state transitions of cache entries, a Temporal Stability Index (TSI) to measure the temporal locality of each entry, and a Dynamic Frequency Mapping (DFM) to record access frequencies. Additionally, a Predictive Heuristic Realignment (PHR) component is used to adjust predictions based on historical patterns.
QTM = defaultdict(lambda: defaultdict(int))
TSI = defaultdict(int)
DFM = defaultdict(int)
PHR = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score from the TSI and DFM, adjusted by the PHR. The QTM is used to predict future access patterns, and entries with low predicted future access are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = TSI[key] + DFM[key] - PHR[key]
        predicted_access = sum(QTM[key].values())
        
        if predicted_access < min_score:
            min_score = predicted_access
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the TSI of the accessed entry is increased to reflect its temporal stability, and the DFM is updated to increase its frequency count. The QTM is adjusted to reflect the transition to a more stable state, and the PHR is realigned to improve future predictions based on this hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    TSI[key] += 1
    DFM[key] += 1
    QTM[key][cache_snapshot.access_count] += 1
    PHR[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the TSI is initialized to a moderate value to allow for quick adaptation, and the DFM is set to a baseline frequency. The QTM is updated to include the new entry's initial state, and the PHR is adjusted to incorporate the potential impact of this new entry on future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    TSI[key] = INITIAL_TSI
    DFM[key] = BASELINE_DFM
    QTM[key][cache_snapshot.access_count] = 1
    PHR[key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QTM is updated to remove the evicted entry's state transitions, and the TSI and DFM are adjusted to reflect the removal. The PHR is recalibrated to account for the change in cache composition, ensuring future predictions remain accurate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in QTM:
        del QTM[key]
    if key in TSI:
        del TSI[key]
    if key in DFM:
        del DFM[key]
    if key in PHR:
        del PHR[key]