# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
INITIAL_QPS = 50
INITIAL_EE = 50
NEUTRAL_NGD = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Phase Shift (QPS) value for each cache entry, representing its temporal relevance, an Entropic Equilibrium (EE) score indicating the entry's stability within the cache, and a Neural Gradient Descent (NGD) vector that adapts based on access patterns. Additionally, a Temporal Vector Mapping (TVM) is used to track the chronological order of accesses.
QPS = defaultdict(lambda: INITIAL_QPS)
EE = defaultdict(lambda: INITIAL_EE)
NGD = defaultdict(lambda: NEUTRAL_NGD)
TVM = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined QPS and EE score, adjusted by the NGD vector to account for recent access trends. The TVM helps ensure that older entries with low relevance are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in TVM:
        score = QPS[key] + EE[key] - NGD[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QPS value of the accessed entry is increased to reflect its current relevance, while the EE score is adjusted to reflect its stability. The NGD vector is updated to reinforce the access pattern, and the TVM is reordered to place the accessed entry at the forefront.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QPS[key] += 10  # Increase QPS to reflect relevance
    EE[key] += 5    # Adjust EE to reflect stability
    NGD[key] += 1   # Update NGD to reinforce access pattern
    
    # Reorder TVM to place the accessed entry at the forefront
    if key in TVM:
        TVM.remove(key)
    TVM.appendleft(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QPS is initialized to a moderate value, the EE score is set to a baseline indicating initial stability, and the NGD vector is initialized to be neutral. The TVM is updated to include the new entry at the most recent position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QPS[key] = INITIAL_QPS
    EE[key] = INITIAL_EE
    NGD[key] = NEUTRAL_NGD
    
    # Update TVM to include the new entry at the most recent position
    TVM.appendleft(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QPS and EE scores of remaining entries are recalibrated to reflect the new cache state, and the NGD vector is adjusted to account for the change in access dynamics. The TVM is updated to remove the evicted entry and maintain the chronological order of remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove the evicted entry from TVM
    if evicted_key in TVM:
        TVM.remove(evicted_key)
    
    # Recalibrate QPS and EE scores for remaining entries
    for key in cache_snapshot.cache:
        QPS[key] = max(0, QPS[key] - 5)  # Decrease QPS slightly
        EE[key] = max(0, EE[key] - 2)    # Decrease EE slightly
        NGD[key] = max(0, NGD[key] - 1)  # Adjust NGD slightly