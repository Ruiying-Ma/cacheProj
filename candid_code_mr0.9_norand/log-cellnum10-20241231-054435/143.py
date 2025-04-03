# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_QFD = 1
INITIAL_NOP = 1
INITIAL_TSI = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Frequency Dynamics (QFD) score for each cache entry, a Neural Oscillation Pattern (NOP) index, and a Temporal Stability Index (TSI). The QFD score reflects the frequency and recency of access, the NOP index captures the rhythmic access patterns, and the TSI measures the consistency of access over time.
qfd_scores = defaultdict(lambda: BASELINE_QFD)
nop_indices = defaultdict(lambda: INITIAL_NOP)
tsi_values = defaultdict(lambda: INITIAL_TSI)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest combined score of QFD, NOP, and TSI. This approach ensures that entries with infrequent, irregular, and unstable access patterns are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = qfd_scores[key] + nop_indices[key] + tsi_values[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QFD score is incremented to reflect increased frequency, the NOP index is adjusted to align with the detected access rhythm, and the TSI is recalculated to account for the stability of the access pattern over time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    qfd_scores[key] += 1
    nop_indices[key] = (nop_indices[key] + 1) % 10  # Example adjustment
    tsi_values[key] = cache_snapshot.access_count - (cache_snapshot.access_count % 10)  # Example recalculation

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QFD score is initialized to a baseline value, the NOP index is set to reflect the initial access pattern, and the TSI is calculated to establish an initial stability measure based on the insertion time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    qfd_scores[key] = BASELINE_QFD
    nop_indices[key] = INITIAL_NOP
    tsi_values[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the QFD scores of remaining entries to ensure balance, adjusts the NOP indices to reflect the new cache state, and updates the TSI values to maintain accurate stability assessments.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        qfd_scores[key] = max(BASELINE_QFD, qfd_scores[key] - 1)
        nop_indices[key] = (nop_indices[key] + 1) % 10  # Example adjustment
        tsi_values[key] = cache_snapshot.access_count - (cache_snapshot.access_count % 10)  # Example recalibration