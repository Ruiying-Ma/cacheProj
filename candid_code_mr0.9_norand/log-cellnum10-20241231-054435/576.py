# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QTI_DECREASE_ON_HIT = 0.1
QTI_INCREASE_ON_EVICT = 0.2
INITIAL_QTI = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Turbulence Index (QTI) for each cache entry, a Temporal Synchronization Loop (TSL) counter, and an Entropic Divergence Index (EDI) for the entire cache. The QTI measures the 'quantum turbulence' or volatility of access patterns for each entry, the TSL tracks the temporal alignment of access patterns, and the EDI quantifies the overall disorder in access frequencies.
QTI = defaultdict(lambda: INITIAL_QTI)
TSL = defaultdict(int)
EDI = 0

def calculate_edi(cache_snapshot):
    # Recalculate the EDI based on current cache state
    global EDI
    total_accesses = cache_snapshot.access_count
    if total_accesses == 0:
        EDI = 0
    else:
        EDI = sum((QTI[obj.key] / total_accesses) for obj in cache_snapshot.cache.values())

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest QTI, indicating the most volatile access pattern, and the lowest TSL, suggesting it is least synchronized with current access trends. If there is a tie, the entry contributing most to the EDI is chosen.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_qti = -1
    min_tsl = float('inf')
    max_edi_contribution = -1

    for key, cached_obj in cache_snapshot.cache.items():
        if QTI[key] > max_qti or (QTI[key] == max_qti and TSL[key] < min_tsl):
            max_qti = QTI[key]
            min_tsl = TSL[key]
            candid_obj_key = key
            max_edi_contribution = QTI[key] / cache_snapshot.access_count
        elif QTI[key] == max_qti and TSL[key] == min_tsl:
            edi_contribution = QTI[key] / cache_snapshot.access_count
            if edi_contribution > max_edi_contribution:
                candid_obj_key = key
                max_edi_contribution = edi_contribution

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QTI of the accessed entry is decreased slightly to reflect its stability, the TSL is incremented to enhance its synchronization, and the EDI is recalculated to reflect the reduced disorder due to the hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    QTI[obj.key] = max(0, QTI[obj.key] - QTI_DECREASE_ON_HIT)
    TSL[obj.key] += 1
    calculate_edi(cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its QTI is initialized to a moderate level, the TSL is set to zero, and the EDI is recalculated to account for the new entry's impact on overall cache disorder.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    QTI[obj.key] = INITIAL_QTI
    TSL[obj.key] = 0
    calculate_edi(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the EDI is recalculated to reflect the reduced disorder, and the TSL counters of remaining entries are adjusted to maintain temporal alignment, while the QTI of all entries is slightly increased to reflect the increased volatility due to the change.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        QTI[key] += QTI_INCREASE_ON_EVICT
        TSL[key] = max(0, TSL[key] - 1)
    calculate_edi(cache_snapshot)