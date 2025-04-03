# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
from collections import defaultdict
import math

# Put tunable constant parameters below
INITIAL_CLUSTER_ID = 0
INITIAL_ACCESS_FREQUENCY = 1
INITIAL_RECENCY = 0
INITIAL_GENETIC_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a cluster identifier for each cached object. Additionally, it keeps a probabilistic model of access patterns and a genetic algorithm-based score for each object.
metadata = {
    'access_frequency': defaultdict(lambda: INITIAL_ACCESS_FREQUENCY),
    'recency': defaultdict(lambda: INITIAL_RECENCY),
    'cluster_id': defaultdict(lambda: INITIAL_CLUSTER_ID),
    'genetic_score': defaultdict(lambda: INITIAL_GENETIC_SCORE),
    'probabilistic_model': defaultdict(lambda: 0.0)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first clustering the cached objects based on their access patterns. Within each cluster, it uses a probabilistic model to predict future accesses and selects the object with the lowest genetic algorithm-based score for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    clusters = defaultdict(list)
    for key, cached_obj in cache_snapshot.cache.items():
        clusters[metadata['cluster_id'][key]].append(cached_obj)
    
    min_score = float('inf')
    for cluster in clusters.values():
        for cached_obj in cluster:
            key = cached_obj.key
            score = metadata['genetic_score'][key]
            if score < min_score:
                min_score = score
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency and recency of the accessed object. It also recalculates the object's genetic algorithm-based score and updates the probabilistic model to reflect the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['genetic_score'][key] = calculate_genetic_score(key)
    metadata['probabilistic_model'][key] = update_probabilistic_model(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial cluster identifier based on its access pattern, initializes its access frequency and recency, and calculates an initial genetic algorithm-based score. The probabilistic model is updated to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['access_frequency'][key] = INITIAL_ACCESS_FREQUENCY
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['cluster_id'][key] = INITIAL_CLUSTER_ID
    metadata['genetic_score'][key] = calculate_genetic_score(key)
    metadata['probabilistic_model'][key] = update_probabilistic_model(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes its metadata from the cache, updates the cluster configurations, and adjusts the probabilistic model to account for the removal. The genetic algorithm-based scores of remaining objects are recalculated if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['recency'][evicted_key]
    del metadata['cluster_id'][evicted_key]
    del metadata['genetic_score'][evicted_key]
    del metadata['probabilistic_model'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['genetic_score'][key] = calculate_genetic_score(key)

def calculate_genetic_score(key):
    '''
    This function calculates the genetic algorithm-based score for a given object key.
    - Args:
        - `key`: The key of the object.
    - Return:
        - `score`: The calculated genetic algorithm-based score.
    '''
    # Example calculation (this can be adjusted based on the specific genetic algorithm used)
    frequency = metadata['access_frequency'][key]
    recency = metadata['recency'][key]
    score = 1 / (1 + math.log(1 + frequency)) + 1 / (1 + recency)
    return score

def update_probabilistic_model(key):
    '''
    This function updates the probabilistic model for a given object key.
    - Args:
        - `key`: The key of the object.
    - Return:
        - `probability`: The updated probability of future access.
    '''
    # Example update (this can be adjusted based on the specific probabilistic model used)
    frequency = metadata['access_frequency'][key]
    total_accesses = sum(metadata['access_frequency'].values())
    probability = frequency / total_accesses if total_accesses > 0 else 0
    return probability