# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PREDICTIVE_WEIGHT = 0.5
TEMPORAL_WEIGHT = 0.3
ENTROPIC_WEIGHT = 0.2
INITIAL_ENTROPIC_FEEDBACK = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a 'Quantum Convergence Score' for each cache entry, a 'Predictive Variable' indicating future access likelihood, a 'Temporal Constriction Timer' for tracking time since last access, and an 'Entropic Feedback' value representing the randomness of access patterns.
metadata = {
    'quantum_convergence_score': defaultdict(float),
    'predictive_variable': defaultdict(float),
    'temporal_constriction_timer': defaultdict(int),
    'entropic_feedback': defaultdict(float)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Quantum Convergence Score, which is calculated using a weighted combination of the Predictive Variable, Temporal Constriction Timer, and Entropic Feedback.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (PREDICTIVE_WEIGHT * metadata['predictive_variable'][key] +
                 TEMPORAL_WEIGHT * metadata['temporal_constriction_timer'][key] +
                 ENTROPIC_WEIGHT * metadata['entropic_feedback'][key])
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Quantum Convergence Score is increased based on the Predictive Variable, the Temporal Constriction Timer is reset, and the Entropic Feedback is adjusted to reflect the reduced randomness of the access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['quantum_convergence_score'][key] += metadata['predictive_variable'][key]
    metadata['temporal_constriction_timer'][key] = 0
    metadata['entropic_feedback'][key] *= 0.9  # Reduce randomness

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Quantum Convergence Score is initialized based on the Predictive Variable, the Temporal Constriction Timer starts counting from zero, and the Entropic Feedback is set to a neutral value to allow for initial pattern assessment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['quantum_convergence_score'][key] = metadata['predictive_variable'][key]
    metadata['temporal_constriction_timer'][key] = 0
    metadata['entropic_feedback'][key] = INITIAL_ENTROPIC_FEEDBACK

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Predictive Variable for remaining entries based on recent access patterns, adjusts the Temporal Constriction Timer to reflect the new cache state, and updates the Entropic Feedback to account for the change in cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        metadata['predictive_variable'][key] *= 0.95  # Decay predictive variable
        metadata['temporal_constriction_timer'][key] += 1
        metadata['entropic_feedback'][key] *= 1.05  # Increase randomness slightly