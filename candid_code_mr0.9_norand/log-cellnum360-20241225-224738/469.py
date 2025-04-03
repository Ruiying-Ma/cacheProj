# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_ALGO_INSIGHT_INDEX = 1
DEFAULT_DYNAMIC_CASCADE_LEVEL = 0
PREDICTIVE_HORIZON_INCREMENT = 1
FREQUENT_ACCESS_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a Predictive Horizon score for each cache entry, an Algorithmic Insight index that reflects the entry's access pattern, a Dynamic Cascade level indicating its priority tier, and a Contextual Mapping that associates entries with specific usage contexts.
predictive_horizon_scores = defaultdict(int)
algorithmic_insight_indices = defaultdict(lambda: DEFAULT_ALGO_INSIGHT_INDEX)
dynamic_cascade_levels = defaultdict(lambda: DEFAULT_DYNAMIC_CASCADE_LEVEL)
contextual_mappings = defaultdict(set)
access_frequencies = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Predictive Horizon score within the lowest Dynamic Cascade level, while considering the Contextual Mapping to avoid evicting entries that are likely to be accessed soon based on current context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_ph_score = float('inf')
    min_dc_level = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if dynamic_cascade_levels[key] < min_dc_level or (dynamic_cascade_levels[key] == min_dc_level and predictive_horizon_scores[key] < min_ph_score):
            if obj.key not in contextual_mappings[key]:  # Avoid evicting entries likely to be accessed soon
                min_ph_score = predictive_horizon_scores[key]
                min_dc_level = dynamic_cascade_levels[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Predictive Horizon score is increased based on the Algorithmic Insight index, the Dynamic Cascade level is adjusted upwards if the entry is frequently accessed, and the Contextual Mapping is updated to reflect the current context of access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    predictive_horizon_scores[obj.key] += algorithmic_insight_indices[obj.key] * PREDICTIVE_HORIZON_INCREMENT
    access_frequencies[obj.key] += 1
    
    if access_frequencies[obj.key] > FREQUENT_ACCESS_THRESHOLD:
        dynamic_cascade_levels[obj.key] += 1
    
    # Update contextual mapping (assuming current context is represented by access_count)
    contextual_mappings[obj.key].add(cache_snapshot.access_count)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Predictive Horizon score is initialized based on historical access patterns, the Algorithmic Insight index is set to a default value, the Dynamic Cascade level is set to the lowest tier, and the Contextual Mapping is established based on the insertion context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    predictive_horizon_scores[obj.key] = 0  # Initialize based on historical access patterns if available
    algorithmic_insight_indices[obj.key] = DEFAULT_ALGO_INSIGHT_INDEX
    dynamic_cascade_levels[obj.key] = DEFAULT_DYNAMIC_CASCADE_LEVEL
    contextual_mappings[obj.key] = {cache_snapshot.access_count}  # Establish based on insertion context
    access_frequencies[obj.key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Predictive Horizon scores of remaining entries are recalibrated to reflect the new cache state, the Algorithmic Insight indices are adjusted to account for the change in access patterns, and the Dynamic Cascade levels are re-evaluated to ensure optimal prioritization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate Predictive Horizon scores
    for key in cache_snapshot.cache:
        predictive_horizon_scores[key] = max(0, predictive_horizon_scores[key] - 1)
    
    # Adjust Algorithmic Insight indices
    for key in cache_snapshot.cache:
        algorithmic_insight_indices[key] = max(1, algorithmic_insight_indices[key] - 1)
    
    # Re-evaluate Dynamic Cascade levels
    for key in cache_snapshot.cache:
        if access_frequencies[key] < FREQUENT_ACCESS_THRESHOLD:
            dynamic_cascade_levels[key] = max(0, dynamic_cascade_levels[key] - 1)