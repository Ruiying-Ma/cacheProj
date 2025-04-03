# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_SCORE_INIT = 1.0
HEURISTIC_SCORE_NEUTRAL = 1.0
TEMPORAL_SCORE_INIT = 0
ADAPTIVE_FACTOR_INIT = 1.0
ADAPTIVE_FACTOR_ADJUSTMENT = 0.01

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry, a heuristic learning score based on access patterns, and a temporal coherence score that tracks the time since last access. It also keeps a global adaptive optimization factor that adjusts based on overall cache performance.
predictive_scores = defaultdict(lambda: PREDICTIVE_SCORE_INIT)
heuristic_scores = defaultdict(lambda: HEURISTIC_SCORE_NEUTRAL)
temporal_scores = defaultdict(lambda: TEMPORAL_SCORE_INIT)
global_adaptive_factor = ADAPTIVE_FACTOR_INIT

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, combining the predictive score, heuristic learning score, and temporal coherence score, adjusted by the global adaptive optimization factor. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (predictive_scores[key] * heuristic_scores[key] * 
                           (1 + temporal_scores[key]) * global_adaptive_factor)
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score is increased based on the accuracy of previous predictions, the heuristic learning score is updated to reflect the recent access pattern, and the temporal coherence score is reset to zero. The global adaptive optimization factor is slightly adjusted to favor the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] += 1  # Increase predictive score
    heuristic_scores[key] += 1   # Update heuristic score
    temporal_scores[key] = 0     # Reset temporal score
    global global_adaptive_factor
    global_adaptive_factor += ADAPTIVE_FACTOR_ADJUSTMENT  # Adjust global factor

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive score is initialized based on historical data if available, the heuristic learning score is set to a neutral value, and the temporal coherence score is initialized to zero. The global adaptive optimization factor is recalibrated to account for the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_scores[key] = PREDICTIVE_SCORE_INIT  # Initialize predictive score
    heuristic_scores[key] = HEURISTIC_SCORE_NEUTRAL # Set heuristic score to neutral
    temporal_scores[key] = TEMPORAL_SCORE_INIT      # Initialize temporal score
    global global_adaptive_factor
    global_adaptive_factor -= ADAPTIVE_FACTOR_ADJUSTMENT  # Recalibrate global factor

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive scores of remaining entries are adjusted to reflect the change in cache composition, the heuristic learning scores are updated to deprioritize the evicted pattern, and the temporal coherence scores are recalculated to maintain consistency. The global adaptive optimization factor is fine-tuned to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del predictive_scores[evicted_key]
    del heuristic_scores[evicted_key]
    del temporal_scores[evicted_key]
    
    for key in cache_snapshot.cache:
        temporal_scores[key] += 1  # Recalculate temporal scores
    
    global global_adaptive_factor
    global_adaptive_factor -= ADAPTIVE_FACTOR_ADJUSTMENT  # Fine-tune global factor