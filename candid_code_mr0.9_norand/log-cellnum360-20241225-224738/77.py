# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QUANTUM_UNIT = 1
BASELINE_QUANTUM_LATENCY = 10
DEFAULT_COHERENCE_SCORE = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a stratified cache structure with multiple layers, each with its own linear progression counter. It also tracks quantum latency values for each cache line and a coherence score indicating the level of concurrent access.
cache_metadata = {
    'layers': defaultdict(lambda: defaultdict(dict)),  # {layer_id: {obj_key: {'linear_progression': int, 'quantum_latency': int, 'coherence_score': int}}}
    'layer_access_order': [],  # List of layer_ids in order of access
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim for eviction by identifying the cache line with the highest quantum latency and lowest coherence score within the least recently used layer. If a tie occurs, the line with the lowest linear progression counter is chosen.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if not cache_metadata['layer_access_order']:
        return None

    # Find the least recently used layer
    lru_layer_id = cache_metadata['layer_access_order'][0]
    lru_layer = cache_metadata['layers'][lru_layer_id]

    # Find the victim in the LRU layer
    max_latency = -1
    min_coherence = float('inf')
    min_progression = float('inf')

    for obj_key, metadata in lru_layer.items():
        latency = metadata['quantum_latency']
        coherence = metadata['coherence_score']
        progression = metadata['linear_progression']

        if (latency > max_latency or
            (latency == max_latency and coherence < min_coherence) or
            (latency == max_latency and coherence == min_coherence and progression < min_progression)):
            max_latency = latency
            min_coherence = coherence
            min_progression = progression
            candid_obj_key = obj_key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the linear progression counter for the accessed line is incremented, its quantum latency is reduced by a fixed quantum unit, and its coherence score is increased to reflect improved concurrent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    for layer_id, layer in cache_metadata['layers'].items():
        if obj.key in layer:
            metadata = layer[obj.key]
            metadata['linear_progression'] += 1
            metadata['quantum_latency'] = max(0, metadata['quantum_latency'] - QUANTUM_UNIT)
            metadata['coherence_score'] += 1

            # Move the layer to the end to mark it as recently used
            cache_metadata['layer_access_order'].remove(layer_id)
            cache_metadata['layer_access_order'].append(layer_id)
            break

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its linear progression counter to zero, sets its quantum latency to a baseline value, and assigns a default coherence score based on the current layer's average.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    current_layer_id = len(cache_metadata['layers'])
    cache_metadata['layers'][current_layer_id][obj.key] = {
        'linear_progression': 0,
        'quantum_latency': BASELINE_QUANTUM_LATENCY,
        'coherence_score': DEFAULT_COHERENCE_SCORE
    }
    cache_metadata['layer_access_order'].append(current_layer_id)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the linear progression counters of the remaining lines in the affected layer, adjusts the average quantum latency, and updates the coherence scores to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for layer_id, layer in cache_metadata['layers'].items():
        if evicted_obj.key in layer:
            del layer[evicted_obj.key]

            # Recalibrate the remaining lines in the affected layer
            total_latency = 0
            total_coherence = 0
            count = len(layer)

            for metadata in layer.values():
                metadata['linear_progression'] = max(0, metadata['linear_progression'] - 1)
                total_latency += metadata['quantum_latency']
                total_coherence += metadata['coherence_score']

            if count > 0:
                average_latency = total_latency / count
                average_coherence = total_coherence / count

                for metadata in layer.values():
                    metadata['quantum_latency'] = average_latency
                    metadata['coherence_score'] = average_coherence

            # If the layer is empty, remove it from access order
            if not layer:
                cache_metadata['layer_access_order'].remove(layer_id)

            break