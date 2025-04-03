# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math
from collections import defaultdict

# Put tunable constant parameters below
ENTROPY_BASE = 2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data entropy metrics, and dynamic clusters of data objects based on access patterns. It also includes a predictive model that correlates access patterns with future access likelihood.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'data_entropy': {},
    'clusters': defaultdict(set),
    'predictive_model': defaultdict(float)
}

def calculate_entropy(obj):
    # Placeholder for entropy calculation, can be more complex based on actual data
    return -math.log(obj.size, ENTROPY_BASE)

def predict_future_access_likelihood(cluster):
    # Placeholder for predictive model, can be more complex based on actual data
    return metadata['predictive_model'][cluster]

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cluster with the lowest predicted future access likelihood, then selecting the object within that cluster with the highest data entropy and lowest access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_likelihood = float('inf')
    target_cluster = None

    # Identify the cluster with the lowest predicted future access likelihood
    for cluster, objects in metadata['clusters'].items():
        likelihood = predict_future_access_likelihood(cluster)
        if likelihood < min_likelihood:
            min_likelihood = likelihood
            target_cluster = cluster

    # Within the target cluster, find the object with the highest data entropy and lowest access frequency
    max_entropy = -float('inf')
    min_frequency = float('inf')
    for key in metadata['clusters'][target_cluster]:
        obj = cache_snapshot.cache[key]
        entropy = metadata['data_entropy'][key]
        frequency = metadata['access_frequency'][key]
        if entropy > max_entropy or (entropy == max_entropy and frequency < min_frequency):
            max_entropy = entropy
            min_frequency = frequency
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the last access time and increments the access frequency of the accessed object. It also recalculates the data entropy for the object and updates the predictive model with the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['access_frequency'][key] += 1
    metadata['data_entropy'][key] = calculate_entropy(obj)
    # Update predictive model (placeholder)
    cluster = next(cluster for cluster, objects in metadata['clusters'].items() if key in objects)
    metadata['predictive_model'][cluster] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and last access time. It calculates the initial data entropy and assigns the object to a dynamic cluster based on its access pattern. The predictive model is updated to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['access_frequency'][key] = 1
    metadata['data_entropy'][key] = calculate_entropy(obj)
    # Assign to a cluster (placeholder)
    cluster = 'default_cluster'
    metadata['clusters'][cluster].add(key)
    # Update predictive model (placeholder)
    metadata['predictive_model'][cluster] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy removes the object's metadata from the cache. It updates the dynamic cluster to reflect the removal and adjusts the predictive model to account for the change in the cache's composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    # Remove metadata
    del metadata['last_access_time'][key]
    del metadata['access_frequency'][key]
    del metadata['data_entropy'][key]
    # Update cluster
    cluster = next(cluster for cluster, objects in metadata['clusters'].items() if key in objects)
    metadata['clusters'][cluster].remove(key)
    # Update predictive model (placeholder)
    metadata['predictive_model'][cluster] -= 1