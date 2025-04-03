# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
COMPLEXITY_WEIGHT = 0.4
PREDICTIVE_WEIGHT = 0.3
SYNERGY_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains a complexity score for each cache entry, a predictive score based on access patterns, and a synergy score that measures the resource sharing potential with other entries.
complexity_scores = defaultdict(float)
predictive_scores = defaultdict(float)
synergy_scores = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a strategic adaptation score, which is a weighted combination of the complexity, predictive, and synergy scores, and evicts the entry with the lowest score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        complexity = complexity_scores[key]
        predictive = predictive_scores[key]
        synergy = synergy_scores[key]
        
        strategic_score = (COMPLEXITY_WEIGHT * complexity +
                           PREDICTIVE_WEIGHT * predictive +
                           SYNERGY_WEIGHT * synergy)
        
        if strategic_score < min_score:
            min_score = strategic_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the complexity score is decreased slightly to reflect reduced computational overhead, the predictive score is updated based on recent access patterns, and the synergy score is adjusted to reflect any changes in resource sharing potential.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    complexity_scores[key] *= 0.9  # Decrease complexity slightly
    predictive_scores[key] += 1  # Increase predictive score based on access
    synergy_scores[key] *= 1.05  # Adjust synergy score slightly

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the complexity score is initialized based on the object's size and type, the predictive score is set using initial access pattern predictions, and the synergy score is calculated based on potential resource sharing with existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    complexity_scores[key] = obj.size / 1000.0  # Initialize complexity based on size
    predictive_scores[key] = 1  # Initial predictive score
    synergy_scores[key] = 0.5  # Initial synergy score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the predictive and synergy scores of remaining entries to account for the removal of the evicted entry, ensuring that the cache adapts to the new configuration.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in complexity_scores:
        del complexity_scores[evicted_key]
    if evicted_key in predictive_scores:
        del predictive_scores[evicted_key]
    if evicted_key in synergy_scores:
        del synergy_scores[evicted_key]
    
    # Recalibrate scores for remaining entries
    for key in cache_snapshot.cache:
        predictive_scores[key] *= 0.95  # Slightly decrease predictive scores
        synergy_scores[key] *= 0.95  # Slightly decrease synergy scores