# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
TEMPORAL_WEIGHT = 0.4
LOAD_FACTOR_WEIGHT = 0.3
PREDICTIVE_RESONANCE_WEIGHT = 0.3
BASELINE_TEMPORAL_SCORE = 1
INITIAL_LOAD_FACTOR = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a temporal score for each cache entry, a load factor indicating the frequency of access, and a predictive resonance value that estimates future access patterns based on historical data.
temporal_scores = defaultdict(lambda: BASELINE_TEMPORAL_SCORE)
load_factors = defaultdict(lambda: INITIAL_LOAD_FACTOR)
predictive_resonance = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of the temporal score, load factor, and predictive resonance. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (TEMPORAL_WEIGHT * temporal_scores[key] +
                           LOAD_FACTOR_WEIGHT * load_factors[key] +
                           PREDICTIVE_RESONANCE_WEIGHT * predictive_resonance[key])
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal score is incremented to reflect recent access, the load factor is adjusted to account for the increased frequency, and the predictive resonance is updated using a heuristic that considers the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] += 1
    load_factors[key] += 1
    predictive_resonance[key] = (predictive_resonance[key] + 1) / 2  # Simple heuristic

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal score is initialized to a baseline value, the load factor is set to reflect initial access, and the predictive resonance is calculated using initial access patterns and historical data of similar objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] = BASELINE_TEMPORAL_SCORE
    load_factors[key] = INITIAL_LOAD_FACTOR
    predictive_resonance[key] = 0.5  # Assume a neutral initial predictive resonance

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the predictive resonance of remaining entries to account for the change in cache composition, and adjusts the load factors to reflect the reduced competition for cache space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del temporal_scores[evicted_key]
    del load_factors[evicted_key]
    del predictive_resonance[evicted_key]
    
    for key in cache_snapshot.cache:
        load_factors[key] = max(1, load_factors[key] - 1)  # Reduce load factor
        predictive_resonance[key] *= 0.9  # Slightly decay predictive resonance