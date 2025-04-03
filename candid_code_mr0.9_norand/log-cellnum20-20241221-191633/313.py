# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_CONTEXTUAL_PRIORITY = 1.0
NEUTRAL_DYNAMIC_ALLOCATION_WEIGHT = 1.0
LOW_LOAD_HARMONIC = 0.1
INITIAL_PREDICTIVE_ATTAINMENT = 0.5
CONTEXTUAL_PRIORITY_INCREMENT = 0.1
LOAD_HARMONIC_INCREMENT = 0.1
DYNAMIC_ALLOCATION_ADJUSTMENT = 0.05
PREDICTIVE_ATTAINMENT_ADJUSTMENT = 0.05

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including contextual priority scores for each cache entry, dynamic allocation weights, load harmonic values, and predictive attainment scores. Contextual priority scores are based on the importance of the data in the current workload context. Dynamic allocation weights adjust based on cache usage patterns. Load harmonic values track the frequency and recency of access patterns. Predictive attainment scores estimate future access likelihood based on historical data.
contextual_priority_scores = defaultdict(lambda: BASELINE_CONTEXTUAL_PRIORITY)
dynamic_allocation_weights = defaultdict(lambda: NEUTRAL_DYNAMIC_ALLOCATION_WEIGHT)
load_harmonic_values = defaultdict(lambda: LOW_LOAD_HARMONIC)
predictive_attainment_scores = defaultdict(lambda: INITIAL_PREDICTIVE_ATTAINMENT)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of the contextual priority, dynamic allocation weight, load harmonic, and predictive attainment score. The entry with the lowest composite score is selected for eviction, ensuring that the most contextually relevant and likely-to-be-accessed data is retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        composite_score = (
            contextual_priority_scores[key] +
            dynamic_allocation_weights[key] +
            load_harmonic_values[key] +
            predictive_attainment_scores[key]
        )
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the contextual priority score and load harmonic value of the accessed entry, reflecting its current importance and recent access. The dynamic allocation weight is adjusted to favor similar entries, and the predictive attainment score is updated based on the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    contextual_priority_scores[key] += CONTEXTUAL_PRIORITY_INCREMENT
    load_harmonic_values[key] += LOAD_HARMONIC_INCREMENT
    dynamic_allocation_weights[key] += DYNAMIC_ALLOCATION_ADJUSTMENT
    predictive_attainment_scores[key] += PREDICTIVE_ATTAINMENT_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline contextual priority score, a neutral dynamic allocation weight, a low load harmonic value, and a predictive attainment score based on initial access predictions. These values are set to adapt quickly to new access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    contextual_priority_scores[key] = BASELINE_CONTEXTUAL_PRIORITY
    dynamic_allocation_weights[key] = NEUTRAL_DYNAMIC_ALLOCATION_WEIGHT
    load_harmonic_values[key] = LOW_LOAD_HARMONIC
    predictive_attainment_scores[key] = INITIAL_PREDICTIVE_ATTAINMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic allocation weights to redistribute cache space more effectively among remaining entries. It also updates the predictive attainment model to refine future access predictions, ensuring that similar low-priority entries are deprioritized in future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    del contextual_priority_scores[evicted_key]
    del dynamic_allocation_weights[evicted_key]
    del load_harmonic_values[evicted_key]
    del predictive_attainment_scores[evicted_key]
    
    # Recalibrate dynamic allocation weights and predictive attainment scores
    for key in cache_snapshot.cache:
        dynamic_allocation_weights[key] *= (1 - DYNAMIC_ALLOCATION_ADJUSTMENT)
        predictive_attainment_scores[key] *= (1 - PREDICTIVE_ATTAINMENT_ADJUSTMENT)