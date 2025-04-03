# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PEM_SCORE = 1.0
NEUTRAL_THI_VALUE = 0.5
LEARNING_RATE = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Sequential Pattern Analysis table to track access sequences, a Predictive Eviction Model score for each cache entry, a Temporal Harmony Index to measure temporal locality, and a Dynamic Learning Curve to adaptively adjust the importance of each factor over time.
sequential_pattern_analysis = defaultdict(list)
predictive_eviction_model = defaultdict(lambda: INITIAL_PEM_SCORE)
temporal_harmony_index = defaultdict(lambda: NEUTRAL_THI_VALUE)
dynamic_learning_curve = defaultdict(lambda: 1.0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, combining the Predictive Eviction Model score, Temporal Harmony Index, and Sequential Pattern Analysis. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        pem_score = predictive_eviction_model[key]
        thi_score = temporal_harmony_index[key]
        spa_score = len(sequential_pattern_analysis[key])
        
        composite_score = (pem_score * dynamic_learning_curve['pem'] +
                           thi_score * dynamic_learning_curve['thi'] +
                           spa_score * dynamic_learning_curve['spa'])
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Sequential Pattern Analysis table is updated to reflect the new access sequence, the Predictive Eviction Model score is adjusted to decrease the likelihood of future eviction, and the Temporal Harmony Index is recalibrated to reflect improved temporal locality.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    sequential_pattern_analysis[key].append(cache_snapshot.access_count)
    predictive_eviction_model[key] *= (1 - LEARNING_RATE)
    temporal_harmony_index[key] = min(1.0, temporal_harmony_index[key] + LEARNING_RATE)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Sequential Pattern Analysis table is updated to include the new sequence, the Predictive Eviction Model score is initialized based on initial access patterns, and the Temporal Harmony Index is set to a neutral value to allow for rapid adaptation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    sequential_pattern_analysis[key] = [cache_snapshot.access_count]
    predictive_eviction_model[key] = INITIAL_PEM_SCORE
    temporal_harmony_index[key] = NEUTRAL_THI_VALUE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Sequential Pattern Analysis table is pruned to remove outdated sequences, the Predictive Eviction Model is recalibrated to reflect the change in cache composition, and the Dynamic Learning Curve is adjusted to refine the balance between the different metadata factors.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in sequential_pattern_analysis:
        del sequential_pattern_analysis[evicted_key]
    if evicted_key in predictive_eviction_model:
        del predictive_eviction_model[evicted_key]
    if evicted_key in temporal_harmony_index:
        del temporal_harmony_index[evicted_key]
    
    # Adjust the dynamic learning curve
    dynamic_learning_curve['pem'] = max(0.1, dynamic_learning_curve['pem'] - LEARNING_RATE)
    dynamic_learning_curve['thi'] = max(0.1, dynamic_learning_curve['thi'] - LEARNING_RATE)
    dynamic_learning_curve['spa'] = max(0.1, dynamic_learning_curve['spa'] - LEARNING_RATE)