# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
COGNITIVE_FORECAST_INCREMENT = 1
INITIAL_COGNITIVE_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a cognitive forecast score for each cache entry, a temporal linkage map to track access patterns, and a strategic model that predicts future access based on historical data. It also keeps a parallel execution index to manage concurrent access efficiently.
cognitive_forecast_scores = defaultdict(lambda: INITIAL_COGNITIVE_SCORE)
temporal_linkage_map = defaultdict(list)
strategic_model = defaultdict(int)
parallel_execution_index = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest cognitive forecast score, which indicates the least likelihood of future access. It also considers the temporal linkage to ensure that evicting this entry will minimally disrupt the predicted access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = cognitive_forecast_scores[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the cognitive forecast score of the accessed entry is increased, reflecting its continued relevance. The temporal linkage map is updated to strengthen the connection between this entry and the subsequent access pattern. The strategic model is refined to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    cognitive_forecast_scores[obj.key] += COGNITIVE_FORECAST_INCREMENT
    if cache_snapshot.access_count > 0:
        last_accessed_key = temporal_linkage_map[cache_snapshot.access_count - 1]
        temporal_linkage_map[last_accessed_key].append(obj.key)
    temporal_linkage_map[cache_snapshot.access_count] = obj.key
    strategic_model[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its cognitive forecast score based on the strategic model's prediction. The temporal linkage map is updated to include this new entry, and the parallel execution index is adjusted to accommodate the new entry efficiently.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    cognitive_forecast_scores[obj.key] = strategic_model[obj.key]
    temporal_linkage_map[cache_snapshot.access_count] = obj.key
    parallel_execution_index[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the cognitive forecast scores of remaining entries to reflect the changed cache state. The temporal linkage map is adjusted to remove the evicted entry, and the strategic model is updated to learn from the eviction decision.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del cognitive_forecast_scores[evicted_obj.key]
    del temporal_linkage_map[parallel_execution_index[evicted_obj.key]]
    del parallel_execution_index[evicted_obj.key]
    strategic_model[evicted_obj.key] = max(0, strategic_model[evicted_obj.key] - 1)