# Import anything you need below
import numpy as np
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_CONNECTION_STRENGTH = 0.1
CONNECTION_STRENGTH_INCREMENT = 0.05
ATOMIC_DISRUPTION_NEUTRAL = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a Synaptic Matrix, a multi-dimensional array representing the strength of connections between cached items, a Temporal Blueprint that records the access patterns over time, and an Atomic Disruption counter that tracks sudden changes in access frequency. Cognitive Fusion is used to integrate these elements into a cohesive decision-making framework.
synaptic_matrix = defaultdict(lambda: defaultdict(lambda: INITIAL_CONNECTION_STRENGTH))
temporal_blueprint = {}
atomic_disruption_counter = defaultdict(lambda: ATOMIC_DISRUPTION_NEUTRAL)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the item with the weakest connections in the Synaptic Matrix, the least recent access in the Temporal Blueprint, and the highest Atomic Disruption score, indicating it is least likely to be accessed again soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_strength = float('inf')
    min_time = float('inf')
    max_disruption = float('-inf')

    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate the total connection strength for the object
        total_strength = sum(synaptic_matrix[key].values())
        last_access_time = temporal_blueprint.get(key, float('inf'))
        disruption_score = atomic_disruption_counter[key]

        # Determine if this object is a better candidate for eviction
        if (total_strength < min_strength or
            (total_strength == min_strength and last_access_time < min_time) or
            (total_strength == min_strength and last_access_time == min_time and disruption_score > max_disruption)):
            min_strength = total_strength
            min_time = last_access_time
            max_disruption = disruption_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Synaptic Matrix is strengthened for the accessed item and its related items, the Temporal Blueprint is updated to reflect the current time, and the Atomic Disruption counter is decreased to indicate stable access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    # Strengthen connections
    for related_key in synaptic_matrix[obj_key]:
        synaptic_matrix[obj_key][related_key] += CONNECTION_STRENGTH_INCREMENT
        synaptic_matrix[related_key][obj_key] += CONNECTION_STRENGTH_INCREMENT

    # Update temporal blueprint
    temporal_blueprint[obj_key] = cache_snapshot.access_count

    # Decrease atomic disruption counter
    atomic_disruption_counter[obj_key] = max(0, atomic_disruption_counter[obj_key] - 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Synaptic Matrix is initialized with weak connections for the new item, the Temporal Blueprint is updated with the current time for the new item, and the Atomic Disruption counter is set to a neutral value to monitor future access changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    # Initialize weak connections
    for key in cache_snapshot.cache:
        synaptic_matrix[obj_key][key] = INITIAL_CONNECTION_STRENGTH
        synaptic_matrix[key][obj_key] = INITIAL_CONNECTION_STRENGTH

    # Update temporal blueprint
    temporal_blueprint[obj_key] = cache_snapshot.access_count

    # Set atomic disruption counter to neutral
    atomic_disruption_counter[obj_key] = ATOMIC_DISRUPTION_NEUTRAL

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Synaptic Matrix is adjusted to remove connections related to the evicted item, the Temporal Blueprint is purged of the evicted item's history, and the Atomic Disruption counter is recalibrated to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove connections related to the evicted item
    if evicted_key in synaptic_matrix:
        del synaptic_matrix[evicted_key]
    for key in synaptic_matrix:
        if evicted_key in synaptic_matrix[key]:
            del synaptic_matrix[key][evicted_key]

    # Purge temporal blueprint
    if evicted_key in temporal_blueprint:
        del temporal_blueprint[evicted_key]

    # Recalibrate atomic disruption counter
    if evicted_key in atomic_disruption_counter:
        del atomic_disruption_counter[evicted_key]