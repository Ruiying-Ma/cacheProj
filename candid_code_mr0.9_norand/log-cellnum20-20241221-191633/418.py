# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_ENTROPY = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a load vector for each cache line, representing the frequency and recency of access, and an entropy value indicating the randomness of access patterns. It also tracks a harmony state, which is a measure of how well the current cache state aligns with optimal access patterns.
load_vectors = defaultdict(lambda: [0, 0])  # {key: [frequency, recency]}
entropies = defaultdict(lambda: BASELINE_ENTROPY)  # {key: entropy}
harmony_states = defaultdict(float)  # {key: harmony state}

def calculate_entropy(load_vector):
    frequency, recency = load_vector
    if frequency == 0:
        return BASELINE_ENTROPY
    return -frequency * math.log(frequency + 1) + recency

def calculate_harmony_state(load_vector):
    frequency, recency = load_vector
    return frequency + recency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache line with the lowest harmony state, indicating it is least aligned with optimal access patterns. If multiple lines have similar harmony states, the one with the highest entropy is chosen, suggesting unpredictable access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_harmony = float('inf')
    max_entropy = -float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        harmony = harmony_states[key]
        entropy = entropies[key]
        if harmony < min_harmony or (harmony == min_harmony and entropy > max_entropy):
            min_harmony = harmony
            max_entropy = entropy
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the load vector for the accessed line is updated to reflect increased frequency and recency. The entropy value is recalculated to account for the new access pattern, and the harmony state is adjusted to reflect improved alignment with optimal patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    load_vectors[key][0] += 1  # Increase frequency
    load_vectors[key][1] = cache_snapshot.access_count  # Update recency
    entropies[key] = calculate_entropy(load_vectors[key])
    harmony_states[key] = calculate_harmony_state(load_vectors[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the load vector is initialized to reflect a single recent access. The entropy is set to a baseline value, and the harmony state is calculated based on initial alignment with expected access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    load_vectors[key] = [1, cache_snapshot.access_count]  # Initialize load vector
    entropies[key] = BASELINE_ENTROPY
    harmony_states[key] = calculate_harmony_state(load_vectors[key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the harmony state of remaining cache lines is recalculated to reflect the new cache composition. The load vectors and entropy values are adjusted to account for the removal of the evicted line, ensuring the cache adapts to the new state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in load_vectors:
        del load_vectors[evicted_key]
        del entropies[evicted_key]
        del harmony_states[evicted_key]

    for key in cache_snapshot.cache:
        entropies[key] = calculate_entropy(load_vectors[key])
        harmony_states[key] = calculate_harmony_state(load_vectors[key])