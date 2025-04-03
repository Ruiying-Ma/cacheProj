# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_MODULATION_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal vector for each cache entry, representing the access pattern over time, a systemic modulation score indicating the entry's importance in the system, and an entropy value reflecting the randomness of access patterns.
temporal_vectors = defaultdict(list)
modulation_scores = defaultdict(lambda: BASELINE_MODULATION_SCORE)
entropy_values = defaultdict(float)

def calculate_entropy(temporal_vector):
    if not temporal_vector:
        return 0.0
    time_diffs = [temporal_vector[i] - temporal_vector[i - 1] for i in range(1, len(temporal_vector))]
    if not time_diffs:
        return 0.0
    mean_diff = sum(time_diffs) / len(time_diffs)
    entropy = -sum((diff / mean_diff) * math.log(diff / mean_diff) for diff in time_diffs if diff > 0)
    return entropy

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest systemic modulation score, highest entropy, and least recent temporal vectorization, ensuring a balance between importance, predictability, and recency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_modulation_score = float('inf')
    max_entropy = -float('inf')
    oldest_time = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        modulation_score = modulation_scores[key]
        entropy = entropy_values[key]
        last_access_time = temporal_vectors[key][-1] if temporal_vectors[key] else 0

        if (modulation_score < min_modulation_score or
            (modulation_score == min_modulation_score and entropy > max_entropy) or
            (modulation_score == min_modulation_score and entropy == max_entropy and last_access_time < oldest_time)):
            candid_obj_key = key
            min_modulation_score = modulation_score
            max_entropy = entropy
            oldest_time = last_access_time
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal vector of the accessed entry is updated to reflect the current time, the systemic modulation score is incremented to increase its importance, and the entropy value is recalculated to account for the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_vectors[key].append(cache_snapshot.access_count)
    modulation_scores[key] += 1
    entropy_values[key] = calculate_entropy(temporal_vectors[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its temporal vector is initialized with the current time, the systemic modulation score is set to a baseline value, and the entropy is calculated based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_vectors[key] = [cache_snapshot.access_count]
    modulation_scores[key] = BASELINE_MODULATION_SCORE
    entropy_values[key] = calculate_entropy(temporal_vectors[key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the systemic modulation scores of remaining entries to maintain relative importance, adjusts temporal vectors to reflect the new cache state, and updates entropy values to redistribute access randomness across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_vectors:
        del temporal_vectors[evicted_key]
    if evicted_key in modulation_scores:
        del modulation_scores[evicted_key]
    if evicted_key in entropy_values:
        del entropy_values[evicted_key]

    for key in cache_snapshot.cache:
        modulation_scores[key] *= 0.9  # Example recalibration factor
        entropy_values[key] = calculate_entropy(temporal_vectors[key])