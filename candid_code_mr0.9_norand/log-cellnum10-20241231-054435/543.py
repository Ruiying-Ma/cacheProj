# Import anything you need below
import collections

# Put tunable constant parameters below
BASELINE_QFO = 1
NEUTRAL_NDF = 1
QFO_INCREMENT = 1
NDF_DAMPENING_FACTOR = 0.9
AHM_LEARNING_RATE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Quantum Field Oscillation (QFO) values for each cache entry, a Neural Damping Factor (NDF) that adjusts based on access patterns, a Temporal Coherence Loop (TCL) that tracks the temporal access sequence, and an Adaptive Heuristic Mapping (AHM) that learns from past eviction decisions.
QFO = collections.defaultdict(lambda: BASELINE_QFO)
NDF = collections.defaultdict(lambda: NEUTRAL_NDF)
TCL = collections.deque()
AHM = collections.defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score of QFO and NDF, adjusted by the AHM. The TCL ensures that entries with recent coherent access patterns are less likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (QFO[key] + NDF[key]) * (1 - AHM[key])
        if score < min_score and key not in TCL:
            min_score = score
            candid_obj_key = key
    
    if candid_obj_key is None:
        # If all entries are in TCL, evict the least recently used in TCL
        candid_obj_key = TCL.popleft()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QFO of the accessed entry is incremented to reflect its increased relevance, while the NDF is adjusted to dampen the impact of frequent accesses. The TCL is updated to reinforce the temporal sequence, and the AHM is refined based on the success of retaining the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QFO[key] += QFO_INCREMENT
    NDF[key] *= NDF_DAMPENING_FACTOR
    if key in TCL:
        TCL.remove(key)
    TCL.append(key)
    AHM[key] += AHM_LEARNING_RATE * (1 - AHM[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QFO is initialized to a baseline value, the NDF is set to a neutral state, the TCL is updated to include the new entry in the temporal sequence, and the AHM is adjusted to incorporate the new entry's potential impact on future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QFO[key] = BASELINE_QFO
    NDF[key] = NEUTRAL_NDF
    TCL.append(key)
    AHM[key] = 0.5  # Start with a neutral heuristic mapping

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QFO of the evicted entry is reset, the NDF is recalibrated to reflect the change in cache dynamics, the TCL is adjusted to remove the evicted entry from the sequence, and the AHM is updated to learn from the eviction decision, improving future heuristic mappings.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    QFO[evicted_key] = BASELINE_QFO
    NDF[evicted_key] = NEUTRAL_NDF
    if evicted_key in TCL:
        TCL.remove(evicted_key)
    AHM[evicted_key] -= AHM_LEARNING_RATE * AHM[evicted_key]