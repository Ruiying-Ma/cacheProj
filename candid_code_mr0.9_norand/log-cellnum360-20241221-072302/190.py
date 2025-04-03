# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_CONTEXTUAL_TAGS = set()
INITIAL_QUANTUM_SCORE = 0.5
FREQUENCY_MODULATION_WEIGHT = 0.4
CONTEXTUAL_RELEVANCE_WEIGHT = 0.3
QUANTUM_INTERPOLATION_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, contextual tags derived from contextual analytics, quantum interpolation scores for predictive access patterns, and a dynamic synthesis index that combines these factors into a unified score.
metadata = {
    'access_frequency': defaultdict(int),
    'contextual_tags': defaultdict(lambda: INITIAL_CONTEXTUAL_TAGS.copy()),
    'quantum_scores': defaultdict(lambda: INITIAL_QUANTUM_SCORE),
    'dynamic_synthesis_index': defaultdict(float)
}

def calculate_dynamic_synthesis_index(key):
    frequency_modulation = metadata['access_frequency'][key]
    contextual_relevance = len(metadata['contextual_tags'][key])
    quantum_interpolation = metadata['quantum_scores'][key]
    
    return (FREQUENCY_MODULATION_WEIGHT * frequency_modulation +
            CONTEXTUAL_RELEVANCE_WEIGHT * contextual_relevance +
            QUANTUM_INTERPOLATION_WEIGHT * quantum_interpolation)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest dynamic synthesis index, which is calculated by combining the frequency modulation, contextual relevance, and quantum interpolation scores.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_index = float('inf')
    
    for key in cache_snapshot.cache:
        index = calculate_dynamic_synthesis_index(key)
        if index < min_index:
            min_index = index
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency is incremented, the contextual tags are updated based on the current context, the quantum interpolation score is recalculated to reflect the new access pattern, and the dynamic synthesis index is adjusted accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    # Update contextual tags based on current context (not specified, so assume no change)
    # Recalculate quantum interpolation score (not specified, so assume no change)
    metadata['dynamic_synthesis_index'][key] = calculate_dynamic_synthesis_index(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized, contextual tags are assigned based on initial context, a preliminary quantum interpolation score is calculated, and the dynamic synthesis index is set to reflect these initial values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['contextual_tags'][key] = INITIAL_CONTEXTUAL_TAGS.copy()
    metadata['quantum_scores'][key] = INITIAL_QUANTUM_SCORE
    metadata['dynamic_synthesis_index'][key] = calculate_dynamic_synthesis_index(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the quantum interpolation model to improve future predictions, updates contextual analytics to refine tag relevance, and adjusts the dynamic synthesis index of remaining entries to maintain cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Recalibrate quantum interpolation model (not specified, so assume no change)
    # Update contextual analytics (not specified, so assume no change)
    # Remove metadata for evicted object
    del metadata['access_frequency'][evicted_key]
    del metadata['contextual_tags'][evicted_key]
    del metadata['quantum_scores'][evicted_key]
    del metadata['dynamic_synthesis_index'][evicted_key]
    
    # Adjust dynamic synthesis index of remaining entries
    for key in cache_snapshot.cache:
        metadata['dynamic_synthesis_index'][key] = calculate_dynamic_synthesis_index(key)