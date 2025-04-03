# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
COGNITIVE_ALIGNMENT_WEIGHT = 0.4
PREDICTIVE_INTERFACE_WEIGHT = 0.3
TEMPORAL_OSCILLATION_WEIGHT = 0.2
ENTROPIC_FEEDBACK_WEIGHT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a cognitive alignment score, a predictive interface score, a temporal oscillation value, and an entropic feedback measure. These scores are used to assess the relevance, predict future access patterns, track temporal access patterns, and measure randomness in access patterns respectively.
metadata = defaultdict(lambda: {
    'cognitive_alignment': 0,
    'predictive_interface': 0,
    'temporal_oscillation': 0,
    'entropic_feedback': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry using a weighted sum of the cognitive alignment, predictive interface, temporal oscillation, and entropic feedback scores. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        scores = metadata[key]
        composite_score = (
            COGNITIVE_ALIGNMENT_WEIGHT * scores['cognitive_alignment'] +
            PREDICTIVE_INTERFACE_WEIGHT * scores['predictive_interface'] +
            TEMPORAL_OSCILLATION_WEIGHT * scores['temporal_oscillation'] +
            ENTROPIC_FEEDBACK_WEIGHT * scores['entropic_feedback']
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the cognitive alignment score is increased to reflect the relevance of the entry, the predictive interface score is updated based on recent access patterns, the temporal oscillation value is adjusted to reflect the current access time, and the entropic feedback measure is recalibrated to account for the reduced randomness in access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    scores = metadata[obj.key]
    scores['cognitive_alignment'] += 1
    scores['predictive_interface'] += 1
    scores['temporal_oscillation'] = cache_snapshot.access_count
    scores['entropic_feedback'] -= 0.1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the cognitive alignment score is initialized based on initial relevance, the predictive interface score is set using historical access data if available, the temporal oscillation value is initialized to the current time, and the entropic feedback measure is set to a neutral value to allow for future adjustments.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    scores = metadata[obj.key]
    scores['cognitive_alignment'] = 1
    scores['predictive_interface'] = 1
    scores['temporal_oscillation'] = cache_snapshot.access_count
    scores['entropic_feedback'] = 0.5

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the cognitive alignment scores of remaining entries are slightly adjusted to reflect the change in cache composition, the predictive interface scores are recalibrated to account for the removal of the evicted entry, the temporal oscillation values are updated to reflect the new temporal dynamics, and the entropic feedback measures are recalculated to ensure the cache maintains a balanced randomness in access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    del metadata[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        scores = metadata[key]
        scores['cognitive_alignment'] *= 0.9
        scores['predictive_interface'] *= 0.9
        scores['temporal_oscillation'] = cache_snapshot.access_count
        scores['entropic_feedback'] *= 1.1