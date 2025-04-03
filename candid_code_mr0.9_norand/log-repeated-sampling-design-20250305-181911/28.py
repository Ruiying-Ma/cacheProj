# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
TIME_WINDOWS = 5
PRIORITY_LEVELS = 3
INITIAL_IMPORTANCE = 1
INITIAL_COUNT = 1
TIME_DEGRADATION_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Recency-Importance Matrix', a 2D grid where each row represents a time window (recency) and each column represents a priority level of data (importance). Time windows are reset periodically, and each cell records the number of accesses for the corresponding recency and importance.
recency_importance_matrix = [[0 for _ in range(PRIORITY_LEVELS)] for _ in range(TIME_WINDOWS)]
object_metadata = {}  # Maps object key to (time_window, importance_level)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    When eviction is necessary, the policy selects the data corresponding to the position in the matrix with the lowest access count multiplied by a time degradation factor. If multiple candidates exist, the least important (priority level) one is chosen first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        time_window, importance_level = object_metadata[key]
        score = recency_importance_matrix[time_window][importance_level] * (TIME_DEGRADATION_FACTOR ** time_window)
        if score < min_score or (score == min_score and importance_level < object_metadata[candid_obj_key][1]):
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The policy increments the count in the matrix cell corresponding to the time window of the access and the importance level of the accessed data. It also reclassifies the access into the current time window.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    time_window, importance_level = object_metadata[obj.key]
    recency_importance_matrix[time_window][importance_level] += 1
    object_metadata[obj.key] = (0, importance_level)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon insertion, the policy assigns an initial importance level to the new data and places it in the current time window of the matrix. The initialization count is set to a small non-zero value to avoid immediate eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    object_metadata[obj.key] = (0, INITIAL_IMPORTANCE)
    recency_importance_matrix[0][INITIAL_IMPORTANCE] += INITIAL_COUNT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy zeros out the count in the corresponding matrix cell and adjusts the counts throughout the matrix to maintain relative importance across different recency windows.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    time_window, importance_level = object_metadata.pop(evicted_obj.key)
    recency_importance_matrix[time_window][importance_level] = 0
    
    # Adjust counts to maintain relative importance
    for i in range(TIME_WINDOWS):
        for j in range(PRIORITY_LEVELS):
            recency_importance_matrix[i][j] *= TIME_DEGRADATION_FACTOR