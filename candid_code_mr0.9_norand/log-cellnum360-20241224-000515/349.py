# Import anything you need below
import collections

# Put tunable constant parameters below
INITIAL_HEURISTIC_SCORE = 1.0
EFFICIENCY_BOOST_INCREMENT = 0.05
EFFICIENCY_BOOST_DECREMENT = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal map of access patterns, a predictive heuristic score for each cache entry, and an efficiency boost factor that adjusts based on recent cache performance.
temporal_map = collections.defaultdict(int)
heuristic_scores = collections.defaultdict(lambda: INITIAL_HEURISTIC_SCORE)
efficiency_boost_factor = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive heuristic score, adjusted by the efficiency boost factor, and considering the temporal mapping to avoid evicting entries likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        adjusted_score = heuristic_scores[key] * efficiency_boost_factor
        if adjusted_score < min_score and temporal_map[key] < cache_snapshot.access_count:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal map is updated to reflect the current access time, the predictive heuristic score is increased to reflect the likelihood of future accesses, and the efficiency boost factor is adjusted slightly upwards to reflect improved cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global efficiency_boost_factor
    temporal_map[obj.key] = cache_snapshot.access_count
    heuristic_scores[obj.key] += 1
    efficiency_boost_factor += EFFICIENCY_BOOST_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal map is initialized with the current time, the predictive heuristic score is set based on initial access patterns, and the efficiency boost factor is recalibrated to account for the new entry's potential impact on cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global efficiency_boost_factor
    temporal_map[obj.key] = cache_snapshot.access_count
    heuristic_scores[obj.key] = INITIAL_HEURISTIC_SCORE
    efficiency_boost_factor = max(1.0, efficiency_boost_factor - EFFICIENCY_BOOST_DECREMENT)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the temporal map is adjusted to remove the evicted entry, the predictive heuristic scores of remaining entries are recalculated to reflect the new cache state, and the efficiency boost factor is slightly decreased to account for the potential performance impact of the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global efficiency_boost_factor
    if evicted_obj.key in temporal_map:
        del temporal_map[evicted_obj.key]
    if evicted_obj.key in heuristic_scores:
        del heuristic_scores[evicted_obj.key]
    
    efficiency_boost_factor = max(1.0, efficiency_boost_factor - EFFICIENCY_BOOST_DECREMENT)