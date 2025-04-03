# Import anything you need below
from collections import defaultdict, deque
import heapq

# Put tunable constant parameters below
INITIAL_SYSTEMATIC_EXPANSION_SCORE = 1
INITIAL_RECURSIVE_CONTINUITY = 0
LAYER_THRESHOLD_INCREMENT = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-layered priority queue for cache entries, where each layer represents a different priority level. Each entry is associated with a 'systematic expansion' score that increases with usage and a 'proactive alignment' timestamp indicating its last access time. A 'recursive continuity' counter tracks the number of consecutive accesses without eviction.
priority_layers = defaultdict(list)  # Each layer is a min-heap
metadata = {}  # Maps obj.key to (layer, systematic_expansion, proactive_alignment, recursive_continuity)
layer_thresholds = [0]  # Thresholds for each layer

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by first identifying the lowest priority layer with entries. Within this layer, it chooses the entry with the lowest 'systematic expansion' score. If scores are tied, the entry with the oldest 'proactive alignment' timestamp is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    for layer in sorted(priority_layers.keys()):
        if priority_layers[layer]:
            # Find the candidate with the lowest systematic expansion score
            candid_obj_key = heapq.heappop(priority_layers[layer])[1]
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the 'systematic expansion' score of the accessed entry is incremented, and its 'proactive alignment' timestamp is updated to the current time. The 'recursive continuity' counter is also incremented, potentially moving the entry to a higher priority layer if thresholds are met.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    layer, systematic_expansion, _, recursive_continuity = metadata[key]
    
    # Update metadata
    systematic_expansion += 1
    proactive_alignment = cache_snapshot.access_count
    recursive_continuity += 1
    
    # Check if it should move to a higher layer
    if layer + 1 < len(layer_thresholds) and systematic_expansion >= layer_thresholds[layer + 1]:
        layer += 1
    
    # Update the priority queue
    heapq.heappush(priority_layers[layer], (systematic_expansion, key))
    metadata[key] = (layer, systematic_expansion, proactive_alignment, recursive_continuity)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the lowest priority layer with an initial 'systematic expansion' score and 'proactive alignment' timestamp set to the current time. The 'recursive continuity' counter is initialized to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    layer = 0
    systematic_expansion = INITIAL_SYSTEMATIC_EXPANSION_SCORE
    proactive_alignment = cache_snapshot.access_count
    recursive_continuity = INITIAL_RECURSIVE_CONTINUITY
    
    # Insert into the lowest priority layer
    heapq.heappush(priority_layers[layer], (systematic_expansion, key))
    metadata[key] = (layer, systematic_expansion, proactive_alignment, recursive_continuity)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the priority layers by potentially lowering the thresholds for 'systematic expansion' scores and 'recursive continuity' counters, ensuring a balanced distribution of entries across layers. Evicted entries' metadata is discarded.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    # Recalibrate thresholds if needed
    total_entries = sum(len(layer) for layer in priority_layers.values())
    if total_entries < len(layer_thresholds) * LAYER_THRESHOLD_INCREMENT:
        layer_thresholds.append(layer_thresholds[-1] + LAYER_THRESHOLD_INCREMENT)