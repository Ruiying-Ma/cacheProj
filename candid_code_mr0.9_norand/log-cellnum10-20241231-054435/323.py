# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASE_ENTROPY = 1.0
STABILITY_INCREMENT = 0.1
ENTROPY_DECREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Mesh Network to track interdependencies between cached items, a Temporal Data Echo to record access patterns over time, a Dynamic Stability Graph to assess the stability of item access frequencies, and an Entropic Node Amplification to measure the entropy of each item's access pattern.
quantum_mesh_network = defaultdict(set)  # Tracks dependencies between items
temporal_data_echo = {}  # Records last access time for each item
dynamic_stability_graph = defaultdict(lambda: 0.5)  # Stability score for each item
entropic_node_amplification = defaultdict(lambda: BASE_ENTROPY)  # Entropy for each item

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the item with the highest entropy in the Entropic Node Amplification, indicating unpredictable access patterns, while also considering the least stable node in the Dynamic Stability Graph.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_stability = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        entropy = entropic_node_amplification[key]
        stability = dynamic_stability_graph[key]
        
        if entropy > max_entropy or (entropy == max_entropy and stability < min_stability):
            max_entropy = entropy
            min_stability = stability
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Data Echo is updated to reflect the latest access time, the Dynamic Stability Graph is adjusted to increase the stability score of the accessed item, and the Entropic Node Amplification is recalculated to reflect the reduced entropy due to the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    obj_key = obj.key
    temporal_data_echo[obj_key] = cache_snapshot.access_count
    dynamic_stability_graph[obj_key] += STABILITY_INCREMENT
    entropic_node_amplification[obj_key] = max(0, entropic_node_amplification[obj_key] - ENTROPY_DECREMENT)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Quantum Mesh Network is updated to include potential dependencies with existing items, the Temporal Data Echo logs the initial access time, the Dynamic Stability Graph initializes the stability score, and the Entropic Node Amplification sets a baseline entropy value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    obj_key = obj.key
    temporal_data_echo[obj_key] = cache_snapshot.access_count
    dynamic_stability_graph[obj_key] = 0.5
    entropic_node_amplification[obj_key] = BASE_ENTROPY
    
    # Update Quantum Mesh Network with potential dependencies
    for key in cache_snapshot.cache:
        if key != obj_key:
            quantum_mesh_network[obj_key].add(key)
            quantum_mesh_network[key].add(obj_key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Quantum Mesh Network removes the evicted item's connections, the Temporal Data Echo purges its access history, the Dynamic Stability Graph recalibrates to reflect the removal, and the Entropic Node Amplification redistributes entropy values among remaining items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove from Quantum Mesh Network
    for key in quantum_mesh_network[evicted_key]:
        quantum_mesh_network[key].remove(evicted_key)
    del quantum_mesh_network[evicted_key]
    
    # Purge Temporal Data Echo
    del temporal_data_echo[evicted_key]
    
    # Recalibrate Dynamic Stability Graph
    del dynamic_stability_graph[evicted_key]
    
    # Redistribute Entropy
    del entropic_node_amplification[evicted_key]
    for key in cache_snapshot.cache:
        entropic_node_amplification[key] += ENTROPY_DECREMENT / len(cache_snapshot.cache)