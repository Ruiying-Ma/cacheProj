# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_PROB_WEIGHT = 1.0
INITIAL_SYNERGY_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Coherence Matrix (TCM) that records access patterns over time, a Quantum Feedback Register (QFR) that stores probabilistic weights for each cache entry, and an Algorithmic Synergy Score (ASS) that combines historical access frequency and recency.
TCM = defaultdict(lambda: 0)
QFR = defaultdict(lambda: BASELINE_PROB_WEIGHT)
ASS = defaultdict(lambda: INITIAL_SYNERGY_SCORE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry using the TCM, QFR, and ASS. The entry with the lowest score, indicating low temporal coherence, low probabilistic weight, and low synergy, is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = TCM[key] + QFR[key] + ASS[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the TCM is updated to reflect the increased temporal coherence of the accessed entry, the QFR is adjusted to increase the probabilistic weight, and the ASS is recalculated to reflect the increased synergy due to the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    TCM[key] += 1
    QFR[key] += 0.1  # Increase probabilistic weight
    ASS[key] = TCM[key] + QFR[key]  # Recalculate synergy score

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the TCM is initialized to reflect the initial temporal coherence, the QFR is set with a baseline probabilistic weight, and the ASS is calculated to establish an initial synergy score based on the insertion context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    TCM[key] = 1  # Initial temporal coherence
    QFR[key] = BASELINE_PROB_WEIGHT  # Baseline probabilistic weight
    ASS[key] = TCM[key] + QFR[key]  # Initial synergy score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the TCM is adjusted to remove the coherence data of the evicted entry, the QFR is recalibrated to redistribute probabilistic weights among remaining entries, and the ASS is updated to reflect the new cache state without the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del TCM[evicted_key]
    del QFR[evicted_key]
    del ASS[evicted_key]
    
    # Recalibrate QFR for remaining entries
    total_weight = sum(QFR.values())
    for key in QFR:
        QFR[key] = (QFR[key] / total_weight) * BASELINE_PROB_WEIGHT
    
    # Update ASS for remaining entries
    for key in ASS:
        ASS[key] = TCM[key] + QFR[key]