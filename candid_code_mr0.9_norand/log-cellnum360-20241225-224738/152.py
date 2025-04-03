# Import anything you need below
import collections

# Put tunable constant parameters below
BASELINE_TEMPORAL_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive overlay matrix that records access patterns, a temporal score for each cache entry, a strategic filter flag indicating the importance of an entry, and a contextual bifurcation index that categorizes entries based on usage context.
temporal_scores = collections.defaultdict(lambda: BASELINE_TEMPORAL_SCORE)
predictive_overlay_matrix = collections.defaultdict(lambda: collections.defaultdict(int))
strategic_filter_flags = collections.defaultdict(bool)
contextual_bifurcation_indices = collections.defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first applying the strategic filter to exclude high-importance entries, then selecting the entry with the lowest combined temporal score and predictive overlay value, adjusted by the contextual bifurcation index.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if strategic_filter_flags[key]:
            continue
        
        combined_score = (temporal_scores[key] + 
                          predictive_overlay_matrix[key][obj.key] - 
                          contextual_bifurcation_indices[key])
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal score of the accessed entry is incremented, the predictive overlay matrix is updated to reflect the recent access pattern, and the contextual bifurcation index is recalibrated based on the current usage context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    temporal_scores[obj.key] += 1
    for key in cache_snapshot.cache:
        predictive_overlay_matrix[key][obj.key] += 1
    contextual_bifurcation_indices[obj.key] = cache_snapshot.access_count % 10

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its temporal score to a baseline value, updates the predictive overlay matrix to include the new access pattern, and assigns a contextual bifurcation index based on the initial usage context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    temporal_scores[obj.key] = BASELINE_TEMPORAL_SCORE
    for key in cache_snapshot.cache:
        predictive_overlay_matrix[key][obj.key] = 0
        predictive_overlay_matrix[obj.key][key] = 0
    contextual_bifurcation_indices[obj.key] = cache_snapshot.access_count % 10

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive overlay matrix to remove the influence of the evicted entry, adjusts the strategic filter flags if necessary, and rebalances the contextual bifurcation indices to maintain optimal categorization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del temporal_scores[evicted_obj.key]
    del predictive_overlay_matrix[evicted_obj.key]
    for key in predictive_overlay_matrix:
        if evicted_obj.key in predictive_overlay_matrix[key]:
            del predictive_overlay_matrix[key][evicted_obj.key]
    
    if strategic_filter_flags[evicted_obj.key]:
        strategic_filter_flags[evicted_obj.key] = False
    
    del contextual_bifurcation_indices[evicted_obj.key]