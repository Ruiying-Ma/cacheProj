# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
BASE_TCI = 1
INITIAL_PFL = 0
NORMAL_HAD = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Coherence Index (TCI) for each cache entry, a Predictive Feedback Loop (PFL) score, and a Heuristic Anomaly Detection (HAD) flag. Additionally, it uses a Quantum Synchronization Algorithm (QSA) timestamp to track the last synchronization event.
metadata = {
    'TCI': {},  # Temporal Coherence Index
    'PFL': {},  # Predictive Feedback Loop score
    'HAD': {},  # Heuristic Anomaly Detection flag
    'QSA': {}   # Quantum Synchronization Algorithm timestamp
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying entries with the lowest TCI. Among those, it selects the one with the highest HAD flag. If there is a tie, the entry with the oldest QSA timestamp is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_tci = min(metadata['TCI'].values())
    candidates = [key for key, tci in metadata['TCI'].items() if tci == min_tci]
    
    if len(candidates) > 1:
        max_had = max(metadata['HAD'][key] for key in candidates)
        candidates = [key for key in candidates if metadata['HAD'][key] == max_had]
    
    if len(candidates) > 1:
        oldest_qsa = min(metadata['QSA'][key] for key in candidates)
        candidates = [key for key in candidates if metadata['QSA'][key] == oldest_qsa]
    
    candid_obj_key = candidates[0]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the TCI of the accessed entry is incremented, the PFL score is updated based on recent access patterns, and the HAD flag is recalculated. The QSA timestamp is synchronized to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['TCI'][key] += 1
    metadata['PFL'][key] += 1  # Simplified update, can be more complex based on patterns
    metadata['HAD'][key] = 0  # Recalculate HAD flag, simplified to normal
    metadata['QSA'][key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the TCI is initialized to a base value, the PFL score is set based on initial predictive analysis, the HAD flag is set to normal, and the QSA timestamp is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['TCI'][key] = BASE_TCI
    metadata['PFL'][key] = INITIAL_PFL
    metadata['HAD'][key] = NORMAL_HAD
    metadata['QSA'][key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalculates the PFL scores for remaining entries to adjust for the change in cache composition, resets the HAD flags if necessary, and updates the QSA timestamp to reflect the eviction event.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del metadata['TCI'][evicted_key]
    del metadata['PFL'][evicted_key]
    del metadata['HAD'][evicted_key]
    del metadata['QSA'][evicted_key]
    
    for key in metadata['PFL']:
        metadata['PFL'][key] -= 1  # Simplified adjustment, can be more complex
    
    for key in metadata['HAD']:
        metadata['HAD'][key] = 0  # Reset HAD flags if necessary
    
    for key in metadata['QSA']:
        metadata['QSA'][key] = cache_snapshot.access_count  # Update QSA timestamp