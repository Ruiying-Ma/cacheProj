# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import networkx as nx

# Put tunable constant parameters below
RECENCY_WEIGHT = 0.4
FREQUENCY_WEIGHT = 0.3
PREDICTED_ACCESS_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains a graph structure where each node represents a cached object and edges represent access patterns. Additionally, it keeps a diffusion model to predict future access probabilities and a meta-reinforcement learning model to adaptively tune the eviction strategy.
cache_graph = nx.DiGraph()
access_frequency = {}
last_access_time = {}
predicted_access_prob = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses the graph neural network to identify nodes with the lowest future access probabilities as predicted by the diffusion model. The meta-reinforcement learning model dynamically adjusts the weight given to different factors such as recency, frequency, and predicted future access.
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
        recency = cache_snapshot.access_count - last_access_time[key]
        frequency = access_frequency[key]
        predicted_access = predicted_access_prob[key]
        
        score = (RECENCY_WEIGHT * recency) + (FREQUENCY_WEIGHT * frequency) + (PREDICTED_ACCESS_WEIGHT * predicted_access)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the graph by reinforcing the edges connected to the accessed node, adjusts the diffusion model based on the new access pattern, and uses the meta-reinforcement learning model to fine-tune the parameters for future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    last_access_time[key] = cache_snapshot.access_count
    access_frequency[key] += 1
    
    # Update graph edges
    for neighbor in cache_graph.neighbors(key):
        cache_graph[key][neighbor]['weight'] += 1
    
    # Update diffusion model (simplified)
    predicted_access_prob[key] = 1 / (1 + access_frequency[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds a new node to the graph, initializes edges based on initial access patterns, updates the diffusion model to incorporate the new object, and uses the meta-reinforcement learning model to adjust the overall cache strategy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_graph.add_node(key)
    last_access_time[key] = cache_snapshot.access_count
    access_frequency[key] = 1
    predicted_access_prob[key] = 1.0  # Initial high probability
    
    # Initialize edges (simplified)
    for other_key in cache_snapshot.cache:
        if other_key != key:
            cache_graph.add_edge(key, other_key, weight=1)
            cache_graph.add_edge(other_key, key, weight=1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the corresponding node and its edges from the graph, recalibrates the diffusion model to account for the change, and employs the meta-reinforcement learning model to re-optimize the eviction parameters.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key in cache_graph:
        cache_graph.remove_node(key)
    if key in last_access_time:
        del last_access_time[key]
    if key in access_frequency:
        del access_frequency[key]
    if key in predicted_access_prob:
        del predicted_access_prob[key]