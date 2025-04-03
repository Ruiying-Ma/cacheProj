# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import numpy as np

# Put tunable constant parameters below
NOISE_FACTOR = 0.1  # Example noise factor for differential privacy
RETRAIN_INTERVAL = 100  # Example interval for retraining the GNN

# Put the metadata specifically maintained by the policy below. The policy maintains a graph structure where nodes represent cached objects and edges represent access patterns. Each node stores access frequency, recency, and a differential privacy noise factor. Quantum entanglement verification is used to ensure the integrity of the graph structure.
class Node:
    def __init__(self, key, access_count, recency, noise_factor):
        self.key = key
        self.access_count = access_count
        self.recency = recency
        self.noise_factor = noise_factor

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, key, access_count, recency, noise_factor):
        self.nodes[key] = Node(key, access_count, recency, noise_factor)
        self.edges[key] = set()

    def remove_node(self, key):
        if key in self.nodes:
            del self.nodes[key]
            del self.edges[key]
            for k in self.edges:
                self.edges[k].discard(key)

    def update_node(self, key, access_count=None, recency=None, noise_factor=None):
        if key in self.nodes:
            if access_count is not None:
                self.nodes[key].access_count = access_count
            if recency is not None:
                self.nodes[key].recency = recency
            if noise_factor is not None:
                self.nodes[key].noise_factor = noise_factor

    def add_edge(self, from_key, to_key):
        if from_key in self.nodes and to_key in self.nodes:
            self.edges[from_key].add(to_key)

    def get_least_valuable_node(self):
        # Placeholder for GNN prediction logic
        # For simplicity, we use a heuristic based on access_count, recency, and noise_factor
        min_value = float('inf')
        min_key = None
        for key, node in self.nodes.items():
            value = node.access_count - node.recency + node.noise_factor
            if value < min_value:
                min_value = value
                min_key = key
        return min_key

graph = Graph()
last_retrain_time = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses a Graph Neural Network (GNN) to predict the least valuable node for eviction based on access patterns, frequency, recency, and noise factors. The node with the lowest predicted value is chosen as the eviction victim.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = graph.get_least_valuable_node()
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the corresponding node are updated. The differential privacy noise factor is adjusted to maintain privacy. The GNN is retrained periodically to adapt to new access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global last_retrain_time
    key = obj.key
    if key in graph.nodes:
        node = graph.nodes[key]
        node.access_count += 1
        node.recency = cache_snapshot.access_count
        node.noise_factor = NOISE_FACTOR  # Adjust noise factor as needed
        if cache_snapshot.access_count - last_retrain_time >= RETRAIN_INTERVAL:
            # Placeholder for GNN retraining logic
            last_retrain_time = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, a new node is created in the graph with initial access frequency, recency, and a noise factor. Edges are updated to reflect the new access pattern. The GNN is retrained to incorporate the new node.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global last_retrain_time
    key = obj.key
    graph.add_node(key, access_count=1, recency=cache_snapshot.access_count, noise_factor=NOISE_FACTOR)
    # Update edges based on access pattern
    for k in cache_snapshot.cache:
        if k != key:
            graph.add_edge(k, key)
    if cache_snapshot.access_count - last_retrain_time >= RETRAIN_INTERVAL:
        # Placeholder for GNN retraining logic
        last_retrain_time = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the corresponding node and its edges are removed from the graph. The GNN is retrained to adjust to the new graph structure. The differential privacy noise factors of remaining nodes are recalibrated to maintain overall privacy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global last_retrain_time
    evicted_key = evicted_obj.key
    graph.remove_node(evicted_key)
    # Recalibrate noise factors
    for node in graph.nodes.values():
        node.noise_factor = NOISE_FACTOR  # Adjust noise factor as needed
    if cache_snapshot.access_count - last_retrain_time >= RETRAIN_INTERVAL:
        # Placeholder for GNN retraining logic
        last_retrain_time = cache_snapshot.access_count