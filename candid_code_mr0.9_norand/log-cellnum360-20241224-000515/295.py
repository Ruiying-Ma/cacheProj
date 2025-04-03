# Import anything you need below
import collections

# Put tunable constant parameters below
LATENCY_IMPACT_FACTOR = 0.5
THROUGHPUT_OPTIMIZATION_FACTOR = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive iteration score for each cache entry, an efficiency matrix that tracks access patterns and latency impact, and a throughput optimization index that evaluates the overall cache performance.
predictive_iteration_scores = collections.defaultdict(int)
efficiency_matrix = collections.defaultdict(lambda: collections.defaultdict(float))
throughput_optimization_index = 0.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest predictive iteration score, adjusted by the efficiency matrix to account for latency impact and throughput optimization index to ensure minimal performance degradation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_iteration_scores[key]
        adjusted_score = score - (efficiency_matrix[key]['latency'] * LATENCY_IMPACT_FACTOR) + (throughput_optimization_index * THROUGHPUT_OPTIMIZATION_FACTOR)
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive iteration score of the accessed entry is incremented, the efficiency matrix is updated to reflect the improved access pattern, and the throughput optimization index is recalculated to account for the reduced latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_iteration_scores[key] += 1
    efficiency_matrix[key]['latency'] = max(0, efficiency_matrix[key]['latency'] - 1)
    throughput_optimization_index = sum(efficiency_matrix[k]['latency'] for k in cache_snapshot.cache) / len(cache_snapshot.cache)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive iteration score is initialized based on historical data, the efficiency matrix is updated to include the new access pattern, and the throughput optimization index is adjusted to incorporate the potential impact of the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_iteration_scores[key] = 1  # Initialize with a base score
    efficiency_matrix[key]['latency'] = 1  # Initialize latency impact
    throughput_optimization_index = sum(efficiency_matrix[k]['latency'] for k in cache_snapshot.cache) / len(cache_snapshot.cache)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive iteration scores of remaining entries are recalibrated, the efficiency matrix is adjusted to remove the evicted entry's influence, and the throughput optimization index is updated to reflect the cache's new state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in predictive_iteration_scores:
        del predictive_iteration_scores[evicted_key]
    if evicted_key in efficiency_matrix:
        del efficiency_matrix[evicted_key]
    
    throughput_optimization_index = sum(efficiency_matrix[k]['latency'] for k in cache_snapshot.cache) / len(cache_snapshot.cache)