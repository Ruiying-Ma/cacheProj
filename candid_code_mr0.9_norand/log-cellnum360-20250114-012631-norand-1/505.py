# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
PVI_DECREASE_AFTER_HIT = 1
QPC_INCREASE_AFTER_HIT = 1
INITIAL_PVI = 10
NEUTRAL_QPC = 5
INITIAL_ANP = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a Predictive Volatility Index (PVI) for each cache entry, a Quantum Phase Coherence (QPC) score, an Adaptive Neural Pathway (ANP) weight, and a Temporal Sequence Mapping (TSM) log.
PVI = {}
QPC = {}
ANP = {}
TSM = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest PVI, lowest QPC score, and least significant ANP weight, while also considering the TSM log to avoid evicting recently accessed sequences.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_pvi = -1
    min_qpc = float('inf')
    min_anp = float('inf')
    min_tsm = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if PVI[key] > max_pvi or (PVI[key] == max_pvi and QPC[key] < min_qpc) or (PVI[key] == max_pvi and QPC[key] == min_qpc and ANP[key] < min_anp) or (PVI[key] == max_pvi and QPC[key] == min_qpc and ANP[key] == min_anp and TSM[key] < min_tsm):
            max_pvi = PVI[key]
            min_qpc = QPC[key]
            min_anp = ANP[key]
            min_tsm = TSM[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the PVI is decreased slightly, the QPC score is increased to reflect stability, the ANP weight is adjusted based on recent access patterns, and the TSM log is updated to include the current access time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    PVI[key] = max(0, PVI[key] - PVI_DECREASE_AFTER_HIT)
    QPC[key] += QPC_INCREASE_AFTER_HIT
    ANP[key] += 1  # Adjust based on recent access patterns
    TSM[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the PVI is initialized based on predicted access volatility, the QPC score is set to a neutral value, the ANP weight is initialized to reflect initial access probability, and the TSM log is updated to include the insertion time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    PVI[key] = INITIAL_PVI
    QPC[key] = NEUTRAL_QPC
    ANP[key] = INITIAL_ANP
    TSM[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the PVI of remaining entries is recalibrated, the QPC scores are adjusted to reflect the new cache state, the ANP weights are updated to adapt to the new configuration, and the TSM log is purged of the evicted entry's records.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del PVI[evicted_key]
    del QPC[evicted_key]
    del ANP[evicted_key]
    del TSM[evicted_key]
    
    for key in cache_snapshot.cache:
        PVI[key] = max(0, PVI[key] - 1)  # Recalibrate PVI
        QPC[key] = max(0, QPC[key] - 1)  # Adjust QPC scores
        ANP[key] = max(0, ANP[key] - 1)  # Update ANP weights