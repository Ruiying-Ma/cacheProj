# Import anything you need below
import numpy as np

# Put tunable constant parameters below
INITIAL_ACCESS_PROBABILITY = 0.1
DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a vector encoding for each cache entry, representing its access pattern and frequency. A predictive matrix is used to forecast future access probabilities based on historical data. A scheduling algorithm prioritizes cache entries for retention based on their predicted future access and harmonizes data by adjusting the vector encodings to reflect changes in access patterns.
vector_encodings = {}
predictive_matrix = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest predicted future access probability from the predictive matrix, adjusted by the scheduling algorithm to ensure data harmonization across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_probability = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        probability = predictive_matrix.get(key, INITIAL_ACCESS_PROBABILITY)
        if probability < min_probability:
            min_probability = probability
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the vector encoding for the accessed entry is updated to reflect the increased access frequency. The predictive matrix is adjusted to increase the future access probability for this entry, and the scheduling algorithm reprioritizes entries to maintain data harmonization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    vector_encodings[key] = vector_encodings.get(key, 0) + 1
    predictive_matrix[key] = predictive_matrix.get(key, INITIAL_ACCESS_PROBABILITY) * DECAY_FACTOR + (1 - DECAY_FACTOR)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its vector encoding is initialized based on initial access patterns. The predictive matrix is updated to include this new entry with a baseline future access probability, and the scheduling algorithm integrates the new entry into the harmonized data structure.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    vector_encodings[key] = 1
    predictive_matrix[key] = INITIAL_ACCESS_PROBABILITY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the vector encoding and predictive matrix entries for the evicted object are removed. The scheduling algorithm recalibrates the remaining entries to ensure continued data harmonization and optimal prioritization of cache entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in vector_encodings:
        del vector_encodings[evicted_key]
    if evicted_key in predictive_matrix:
        del predictive_matrix[evicted_key]