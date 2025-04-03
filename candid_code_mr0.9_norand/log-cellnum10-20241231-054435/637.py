# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INTERACTION_TUNING_BASE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Causal Influence Matrix to track dependencies between memory accesses, a Memory Access Flux counter to measure the rate of access changes, a Pattern Prediction Index to forecast future access patterns, and an Interaction Tuning parameter to adjust sensitivity to access patterns.
causal_influence_matrix = defaultdict(lambda: defaultdict(float))
memory_access_flux = 0
pattern_prediction_index = defaultdict(float)
interaction_tuning = INTERACTION_TUNING_BASE

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score from the Causal Influence Matrix and Pattern Prediction Index, adjusted by the Interaction Tuning parameter to account for recent Memory Access Flux.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        causal_score = sum(causal_influence_matrix[key].values())
        pattern_score = pattern_prediction_index[key]
        combined_score = causal_score + pattern_score - interaction_tuning * memory_access_flux
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Causal Influence Matrix is updated to strengthen the link between the accessed item and its preceding accesses, the Memory Access Flux counter is incremented, the Pattern Prediction Index is adjusted to reflect the hit, and the Interaction Tuning parameter is fine-tuned based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Strengthen links in the Causal Influence Matrix
    for key in cache_snapshot.cache:
        if key != obj.key:
            causal_influence_matrix[obj.key][key] += 1
    
    # Increment Memory Access Flux
    global memory_access_flux
    memory_access_flux += 1
    
    # Adjust Pattern Prediction Index
    pattern_prediction_index[obj.key] += 1
    
    # Fine-tune Interaction Tuning parameter
    global interaction_tuning
    interaction_tuning = INTERACTION_TUNING_BASE + memory_access_flux / (cache_snapshot.access_count + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Causal Influence Matrix is updated to include potential new dependencies, the Memory Access Flux counter is reset to account for the new entry, the Pattern Prediction Index is recalibrated to include the new object, and the Interaction Tuning parameter is adjusted to accommodate the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Update Causal Influence Matrix
    for key in cache_snapshot.cache:
        if key != obj.key:
            causal_influence_matrix[obj.key][key] = 0
    
    # Reset Memory Access Flux
    global memory_access_flux
    memory_access_flux = 0
    
    # Recalibrate Pattern Prediction Index
    pattern_prediction_index[obj.key] = 0
    
    # Adjust Interaction Tuning parameter
    global interaction_tuning
    interaction_tuning = INTERACTION_TUNING_BASE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Causal Influence Matrix is pruned to remove dependencies related to the evicted item, the Memory Access Flux counter is decremented, the Pattern Prediction Index is recalculated to exclude the evicted object, and the Interaction Tuning parameter is modified to reflect the reduced cache size.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Prune Causal Influence Matrix
    if evicted_obj.key in causal_influence_matrix:
        del causal_influence_matrix[evicted_obj.key]
    
    for key in causal_influence_matrix:
        if evicted_obj.key in causal_influence_matrix[key]:
            del causal_influence_matrix[key][evicted_obj.key]
    
    # Decrement Memory Access Flux
    global memory_access_flux
    memory_access_flux = max(0, memory_access_flux - 1)
    
    # Recalculate Pattern Prediction Index
    if evicted_obj.key in pattern_prediction_index:
        del pattern_prediction_index[evicted_obj.key]
    
    # Modify Interaction Tuning parameter
    global interaction_tuning
    interaction_tuning = INTERACTION_TUNING_BASE - memory_access_flux / (cache_snapshot.access_count + 1)