# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_INVERSE_ACCESS_FREQ = 0.5
WEIGHT_HEURISTIC_CYCLE = 0.3
WEIGHT_TEMPORAL_REFLEX = 0.2
BASELINE_ACCESS_FREQUENCY = 1
INITIAL_HEURISTIC_CYCLE = 1
INITIAL_TEMPORAL_REFLEX = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, heuristic cycle count, predictive buffer size, and temporal reflex score for each cache entry. Access frequency tracks how often an item is accessed, heuristic cycle count measures redundancy patterns, predictive buffer size anticipates future cache needs, and temporal reflex score adjusts based on recent access patterns.
metadata = defaultdict(lambda: {
    'access_frequency': BASELINE_ACCESS_FREQUENCY,
    'heuristic_cycle_count': INITIAL_HEURISTIC_CYCLE,
    'predictive_buffer_size': 0,
    'temporal_reflex_score': INITIAL_TEMPORAL_REFLEX
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of inverse access frequency, heuristic cycle redundancy, and temporal reflex score. The entry with the highest composite score is selected for eviction, ensuring that less frequently accessed, redundant, and temporally irrelevant items are prioritized for removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_composite_score = -1

    for key, cached_obj in cache_snapshot.cache.items():
        access_frequency = metadata[key]['access_frequency']
        heuristic_cycle_count = metadata[key]['heuristic_cycle_count']
        temporal_reflex_score = metadata[key]['temporal_reflex_score']

        composite_score = (
            WEIGHT_INVERSE_ACCESS_FREQ / access_frequency +
            WEIGHT_HEURISTIC_CYCLE * heuristic_cycle_count +
            WEIGHT_TEMPORAL_REFLEX * temporal_reflex_score
        )

        if composite_score > max_composite_score:
            max_composite_score = composite_score
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency of the item is incremented, the heuristic cycle count is adjusted to reflect reduced redundancy, and the temporal reflex score is recalibrated to account for the recent access, potentially increasing its priority in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['access_frequency'] += 1
    metadata[key]['heuristic_cycle_count'] = max(1, metadata[key]['heuristic_cycle_count'] - 1)
    metadata[key]['temporal_reflex_score'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to a baseline value, sets the heuristic cycle count based on initial redundancy analysis, and assigns a predictive buffer size and temporal reflex score based on anticipated access patterns derived from historical data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['access_frequency'] = BASELINE_ACCESS_FREQUENCY
    metadata[key]['heuristic_cycle_count'] = INITIAL_HEURISTIC_CYCLE
    metadata[key]['predictive_buffer_size'] = obj.size
    metadata[key]['temporal_reflex_score'] = INITIAL_TEMPORAL_REFLEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive buffer size to better align with current cache demands, adjusts the heuristic cycle count to reflect changes in redundancy, and updates the temporal reflex score to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Recalibrate predictive buffer size
    metadata[evicted_key]['predictive_buffer_size'] = 0
    # Adjust heuristic cycle count
    metadata[evicted_key]['heuristic_cycle_count'] = max(1, metadata[evicted_key]['heuristic_cycle_count'] - 1)
    # Update temporal reflex score
    metadata[evicted_key]['temporal_reflex_score'] = max(1, metadata[evicted_key]['temporal_reflex_score'] - 1)