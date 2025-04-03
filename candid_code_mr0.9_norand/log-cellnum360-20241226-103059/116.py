# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_TEMPORAL_SYMMETRY = 1
INITIAL_ENTANGLEMENT_INDEX = 1
INITIAL_PREDICTIVE_DECOUPLING = 1
VARIABILITY_ADJUSTER_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Symmetry index for each cache entry, an Entanglement Index that links related entries, a Predictive Decoupling score to anticipate future access patterns, and a Variability Adjuster to account for fluctuations in access frequency.
temporal_symmetry = defaultdict(lambda: INITIAL_TEMPORAL_SYMMETRY)
entanglement_index = defaultdict(lambda: INITIAL_ENTANGLEMENT_INDEX)
predictive_decoupling = defaultdict(lambda: INITIAL_PREDICTIVE_DECOUPLING)
variability_adjuster = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of Temporal Symmetry and Entanglement Index, adjusted by the Variability Adjuster to ensure adaptability to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (temporal_symmetry[key] + entanglement_index[key]) * variability_adjuster
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Symmetry index is incremented to reflect recent access, the Entanglement Index is updated to strengthen links with concurrently accessed entries, and the Predictive Decoupling score is recalibrated based on the latest access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    temporal_symmetry[obj.key] += 1
    entanglement_index[obj.key] += 1
    predictive_decoupling[obj.key] = (predictive_decoupling[obj.key] + 1) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Temporal Symmetry index is initialized to a neutral value, the Entanglement Index is set based on initial access context, and the Predictive Decoupling score is calculated using initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    temporal_symmetry[obj.key] = INITIAL_TEMPORAL_SYMMETRY
    entanglement_index[obj.key] = INITIAL_ENTANGLEMENT_INDEX
    predictive_decoupling[obj.key] = INITIAL_PREDICTIVE_DECOUPLING

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Variability Adjuster is recalibrated to reflect the impact of the eviction on cache dynamics, and the Entanglement Index of related entries is adjusted to account for the removal of the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global variability_adjuster
    variability_adjuster *= (1 + VARIABILITY_ADJUSTER_FACTOR)
    
    for key in cache_snapshot.cache:
        if key != evicted_obj.key:
            entanglement_index[key] = max(1, entanglement_index[key] - 1)