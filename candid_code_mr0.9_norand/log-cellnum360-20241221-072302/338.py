# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_HIERARCHICAL_SCORE = 1
INITIAL_COHERENCE_COUNTER = 1
INITIAL_ENTROPY_HARMONIZATION = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal partition index, a hierarchical predictor score, a dynamic coherence counter, and an entropy harmonization value for each cache line.
temporal_partition_index = defaultdict(int)
hierarchical_predictor_score = defaultdict(lambda: BASELINE_HIERARCHICAL_SCORE)
dynamic_coherence_counter = defaultdict(lambda: INITIAL_COHERENCE_COUNTER)
entropy_harmonization_value = defaultdict(lambda: INITIAL_ENTROPY_HARMONIZATION)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the lowest hierarchical predictor score, adjusted by the dynamic coherence counter and entropy harmonization value to ensure balanced eviction across temporal partitions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (hierarchical_predictor_score[key] - 
                 dynamic_coherence_counter[key] + 
                 entropy_harmonization_value[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal partition index is updated to reflect recent access, the hierarchical predictor score is incremented, the dynamic coherence counter is adjusted to reflect increased coherence, and the entropy harmonization value is recalculated to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_partition_index[key] = cache_snapshot.access_count
    hierarchical_predictor_score[key] += 1
    dynamic_coherence_counter[key] += 1
    entropy_harmonization_value[key] = (hierarchical_predictor_score[key] + 
                                        dynamic_coherence_counter[key]) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal partition index is initialized, the hierarchical predictor score is set to a baseline value, the dynamic coherence counter is initialized to reflect initial coherence, and the entropy harmonization value is set to ensure initial balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_partition_index[key] = cache_snapshot.access_count
    hierarchical_predictor_score[key] = BASELINE_HIERARCHICAL_SCORE
    dynamic_coherence_counter[key] = INITIAL_COHERENCE_COUNTER
    entropy_harmonization_value[key] = INITIAL_ENTROPY_HARMONIZATION

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the temporal partition index of remaining lines is adjusted to reflect the change, the hierarchical predictor scores are recalibrated, the dynamic coherence counters are updated to reflect the new state, and the entropy harmonization values are recalculated to maintain overall cache balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_partition_index:
        del temporal_partition_index[evicted_key]
        del hierarchical_predictor_score[evicted_key]
        del dynamic_coherence_counter[evicted_key]
        del entropy_harmonization_value[evicted_key]
    
    for key in cache_snapshot.cache:
        temporal_partition_index[key] = cache_snapshot.access_count
        hierarchical_predictor_score[key] = max(BASELINE_HIERARCHICAL_SCORE, hierarchical_predictor_score[key] - 1)
        dynamic_coherence_counter[key] = max(INITIAL_COHERENCE_COUNTER, dynamic_coherence_counter[key] - 1)
        entropy_harmonization_value[key] = (hierarchical_predictor_score[key] + dynamic_coherence_counter[key]) / 2