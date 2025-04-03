# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_TEMPORAL_SCORE = 1
NEUTRAL_STRATEGIC_INDEX = 0.5
CONTEXTUAL_TAG_WEIGHT = 1.0
PREDICTIVE_WEIGHT_BASE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including temporal scores, contextual tags, predictive weights, and strategic assimilation indices for each cache entry. Temporal scores track the recency and frequency of access, contextual tags capture the usage context, predictive weights estimate future access likelihood, and strategic assimilation indices measure the integration of an entry within the cache ecosystem.
temporal_scores = defaultdict(lambda: BASELINE_TEMPORAL_SCORE)
contextual_tags = defaultdict(lambda: CONTEXTUAL_TAG_WEIGHT)
predictive_weights = defaultdict(lambda: PREDICTIVE_WEIGHT_BASE)
strategic_indices = defaultdict(lambda: NEUTRAL_STRATEGIC_INDEX)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, combining inverse temporal scores, contextual resonance mismatches, low predictive weights, and weak strategic assimilation indices. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        inverse_temporal_score = 1 / temporal_scores[key]
        contextual_mismatch = abs(contextual_tags[key] - CONTEXTUAL_TAG_WEIGHT)
        low_predictive_weight = 1 - predictive_weights[key]
        weak_strategic_index = 1 - strategic_indices[key]
        
        composite_score = (inverse_temporal_score + contextual_mismatch +
                           low_predictive_weight + weak_strategic_index)
        
        if composite_score < lowest_composite_score:
            lowest_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal score of the accessed entry is increased, its contextual tag is reinforced, the predictive weight is adjusted upwards based on recent access patterns, and the strategic assimilation index is recalibrated to reflect its enhanced role in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] += 1
    contextual_tags[key] += 0.1  # Reinforce contextual tag
    predictive_weights[key] = min(1.0, predictive_weights[key] + 0.1)
    strategic_indices[key] = min(1.0, strategic_indices[key] + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its temporal score is initialized to a baseline value, a contextual tag is assigned based on the insertion context, a predictive weight is estimated using initial access patterns, and a strategic assimilation index is set to a neutral value to allow for future adjustment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_scores[key] = BASELINE_TEMPORAL_SCORE
    contextual_tags[key] = CONTEXTUAL_TAG_WEIGHT
    predictive_weights[key] = PREDICTIVE_WEIGHT_BASE
    strategic_indices[key] = NEUTRAL_STRATEGIC_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the strategic assimilation indices of remaining entries to reflect the new cache composition, adjusts contextual tags to account for the removed context, and updates predictive weights to better anticipate future access patterns without the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    for key in cache_snapshot.cache:
        if key != evicted_key:
            strategic_indices[key] = max(0.0, strategic_indices[key] - 0.1)
            contextual_tags[key] = max(0.0, contextual_tags[key] - 0.05)
            predictive_weights[key] = max(0.0, predictive_weights[key] - 0.05)