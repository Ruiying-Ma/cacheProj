# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_QII = 1
INITIAL_NPC = 1
INITIAL_ESM = 1
INITIAL_TDA = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Interaction Index (QII) to measure the interaction strength between cache entries, a Neural Pathway Convergence (NPC) score to track the alignment of access patterns, an Entropic Stability Matrix (ESM) to assess the stability of cache states, and a Temporal Drift Analysis (TDA) to monitor the temporal access patterns.
QII = defaultdict(lambda: INITIAL_QII)
NPC = defaultdict(lambda: INITIAL_NPC)
ESM = defaultdict(lambda: INITIAL_ESM)
TDA = defaultdict(lambda: INITIAL_TDA)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score of QII and NPC, adjusted by the ESM to ensure stability, and further refined by TDA to account for recent temporal access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (QII[key] + NPC[key]) / ESM[key] + TDA[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QII is incremented to reflect increased interaction strength, the NPC score is adjusted to reflect improved alignment, the ESM is recalibrated to maintain stability, and the TDA is updated to reflect the recent access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QII[key] += 1
    NPC[key] += 0.1  # Example adjustment
    ESM[key] *= 0.9  # Example recalibration
    TDA[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QII is initialized based on initial interaction potential, the NPC score is set to a baseline reflecting initial alignment, the ESM is updated to incorporate the new entry's impact on stability, and the TDA is initialized to track the new entry's temporal pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QII[key] = INITIAL_QII
    NPC[key] = INITIAL_NPC
    ESM[key] = INITIAL_ESM
    TDA[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QII is recalculated to remove the evicted entry's influence, the NPC score is adjusted to reflect the new alignment landscape, the ESM is updated to ensure continued stability, and the TDA is recalibrated to remove the evicted entry's temporal data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del QII[evicted_key]
    del NPC[evicted_key]
    del ESM[evicted_key]
    del TDA[evicted_key]