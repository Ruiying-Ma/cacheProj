# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
SCORE_INCREMENT = 0.5
LOAD_STABILIZATION_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a global index of access patterns, predictive scores for each cache entry, and a load stabilization factor that adapts based on current system load and access frequency.
global_access_index = defaultdict(int)
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
load_stabilization_factor = LOAD_STABILIZATION_FACTOR

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive score, adjusted by the load stabilization factor, ensuring that entries likely to be accessed soon are retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = predictive_scores[key] - load_stabilization_factor
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score for the accessed entry is increased, and the global index is updated to reflect the new access pattern, while the load stabilization factor is adjusted to reflect the current system load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    predictive_scores[obj.key] += SCORE_INCREMENT
    global_access_index[obj.key] += 1
    load_stabilization_factor = LOAD_STABILIZATION_FACTOR * (cache_snapshot.size / cache_snapshot.capacity)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial predictive score based on the global index and updates the load stabilization factor to account for the new entry, ensuring balanced cache utilization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    predictive_scores[obj.key] = INITIAL_PREDICTIVE_SCORE + global_access_index[obj.key]
    load_stabilization_factor = LOAD_STABILIZATION_FACTOR * (cache_snapshot.size / cache_snapshot.capacity)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the global index is updated to remove the evicted entry's pattern, and the load stabilization factor is recalibrated to reflect the reduced cache load, maintaining optimal performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in global_access_index:
        del global_access_index[evicted_obj.key]
    if evicted_obj.key in predictive_scores:
        del predictive_scores[evicted_obj.key]
    load_stabilization_factor = LOAD_STABILIZATION_FACTOR * (cache_snapshot.size / cache_snapshot.capacity)