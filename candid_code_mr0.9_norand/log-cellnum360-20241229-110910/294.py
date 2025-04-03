# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FLUX_SCORE = 1
NEUTRAL_FEEDBACK_COUNTER = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including spatial locality vectors, computational flux scores, neural pathway activation levels, and feedback loop counters for each cache entry.
metadata = {
    'spatial_locality': defaultdict(lambda: 0),
    'computational_flux': defaultdict(lambda: BASELINE_FLUX_SCORE),
    'neural_pathway_activation': defaultdict(lambda: 0),
    'feedback_loop_counter': defaultdict(lambda: NEUTRAL_FEEDBACK_COUNTER)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest combined score of spatial locality, computational flux, and neural pathway activation, adjusted by feedback loop counters to ensure dynamic adaptability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (
            metadata['spatial_locality'][key] +
            metadata['computational_flux'][key] +
            metadata['neural_pathway_activation'][key] -
            metadata['feedback_loop_counter'][key]
        )
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the spatial locality vector is reinforced, the computational flux score is incremented, the neural pathway activation level is heightened, and the feedback loop counter is adjusted to reflect the increased relevance of the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['spatial_locality'][key] += 1
    metadata['computational_flux'][key] += 1
    metadata['neural_pathway_activation'][key] += 1
    metadata['feedback_loop_counter'][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the spatial locality vector is initialized based on neighboring entries, the computational flux score is set to a baseline value, the neural pathway activation is primed, and the feedback loop counter is set to a neutral state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Initialize spatial locality based on neighboring entries
    metadata['spatial_locality'][key] = sum(
        metadata['spatial_locality'][neighbor_key] for neighbor_key in cache_snapshot.cache
    ) / (len(cache_snapshot.cache) or 1)
    metadata['computational_flux'][key] = BASELINE_FLUX_SCORE
    metadata['neural_pathway_activation'][key] = 1
    metadata['feedback_loop_counter'][key] = NEUTRAL_FEEDBACK_COUNTER

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the spatial locality vectors of neighboring entries are recalibrated, computational flux scores are redistributed, neural pathway mappings are adjusted to reduce reliance on the evicted entry, and feedback loop counters are updated to reflect the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    for key in cache_snapshot.cache:
        metadata['spatial_locality'][key] = max(0, metadata['spatial_locality'][key] - metadata['spatial_locality'][evicted_key] / 2)
        metadata['computational_flux'][key] = max(BASELINE_FLUX_SCORE, metadata['computational_flux'][key] - 1)
        metadata['neural_pathway_activation'][key] = max(0, metadata['neural_pathway_activation'][key] - 1)
        metadata['feedback_loop_counter'][key] = max(NEUTRAL_FEEDBACK_COUNTER, metadata['feedback_loop_counter'][key] - 1)