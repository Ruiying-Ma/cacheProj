# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_QFO = 1
NEUTRAL_EWS = 1
DEFAULT_NSM = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Frequency Oscillation (QFO) value for each cache entry, an Entropic Wavefront Shift (EWS) score, a Neural Stability Mapping (NSM) index, and a Temporal Cohesion Matrix (TCM) that tracks temporal access patterns.
QFO = defaultdict(lambda: BASELINE_QFO)
EWS = defaultdict(lambda: NEUTRAL_EWS)
NSM = defaultdict(lambda: DEFAULT_NSM)
TCM = defaultdict(lambda: 0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score of QFO and EWS, adjusted by the NSM index. The TCM is used to ensure that entries with high temporal cohesion are less likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (QFO[key] + EWS[key]) / NSM[key] - TCM[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QFO value is incremented to reflect increased access frequency, the EWS score is adjusted to reflect reduced entropy, the NSM index is recalibrated to enhance stability, and the TCM is updated to strengthen temporal links with recent accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QFO[key] += 1
    EWS[key] = max(1, EWS[key] - 1)
    NSM[key] += 1
    TCM[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QFO is initialized to a baseline frequency, the EWS score is set to a neutral entropy level, the NSM index is mapped to a default stability state, and the TCM is updated to include the new entry's temporal position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QFO[key] = BASELINE_QFO
    EWS[key] = NEUTRAL_EWS
    NSM[key] = DEFAULT_NSM
    TCM[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QFO values of remaining entries are normalized, the EWS scores are recalculated to account for the change in cache entropy, the NSM indices are adjusted to maintain overall stability, and the TCM is updated to remove the evicted entry's temporal influence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del QFO[evicted_key]
    del EWS[evicted_key]
    del NSM[evicted_key]
    del TCM[evicted_key]
    
    total_qfo = sum(QFO.values())
    if total_qfo > 0:
        for key in cache_snapshot.cache:
            QFO[key] = QFO[key] / total_qfo * len(cache_snapshot.cache)
    
    for key in cache_snapshot.cache:
        EWS[key] = max(1, EWS[key] - 1)
        NSM[key] = max(1, NSM[key] - 1)