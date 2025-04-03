# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_ENTROPY_SCORE = 100.0
NEUTRAL_INTERACTIVE_SCORE = 0.0

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive map of access patterns using Temporal Vectors, which capture the time intervals between accesses for each cache object. It also tracks an entropy score for each object, representing the randomness of its access pattern, and an interactive score that adjusts based on user interaction patterns.
temporal_vectors = defaultdict(list)
entropy_scores = defaultdict(lambda: DEFAULT_ENTROPY_SCORE)
interactive_scores = defaultdict(lambda: NEUTRAL_INTERACTIVE_SCORE)

def calculate_entropy(temporal_vector):
    if not temporal_vector:
        return DEFAULT_ENTROPY_SCORE
    # Calculate entropy as a measure of unpredictability
    frequency = defaultdict(int)
    for interval in temporal_vector:
        frequency[interval] += 1
    total_intervals = len(temporal_vector)
    entropy = -sum((count / total_intervals) * math.log2(count / total_intervals) for count in frequency.values())
    return entropy

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the highest entropy score, indicating the least predictable access pattern, and the lowest interactive score, suggesting minimal user engagement. Temporal Vectors are used to predict future accesses, and objects with less imminent predicted accesses are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_entropy = -1
    min_interactive_score = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        entropy = entropy_scores[key]
        interactive_score = interactive_scores[key]
        if (entropy > max_entropy) or (entropy == max_entropy and interactive_score < min_interactive_score):
            max_entropy = entropy
            min_interactive_score = interactive_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Vector for the accessed object is updated to reflect the new time interval since its last access. The entropy score is recalculated to account for the updated access pattern, and the interactive score is incremented to reflect increased user engagement.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    last_access_time = temporal_vectors[obj.key][-1] if temporal_vectors[obj.key] else current_time
    interval = current_time - last_access_time
    temporal_vectors[obj.key].append(interval)
    entropy_scores[obj.key] = calculate_entropy(temporal_vectors[obj.key])
    interactive_scores[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its Temporal Vector is initialized based on the current time, and its entropy score is set to a default high value due to lack of historical data. The interactive score is initialized to a neutral value, awaiting further user interaction data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    temporal_vectors[obj.key] = [current_time]
    entropy_scores[obj.key] = DEFAULT_ENTROPY_SCORE
    interactive_scores[obj.key] = NEUTRAL_INTERACTIVE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the entropy scores of remaining objects to account for the changed cache state. The predictive map is adjusted to remove the evicted object's Temporal Vector, and interactive scores are normalized to maintain relative user engagement levels.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in temporal_vectors:
        del temporal_vectors[evicted_obj.key]
    if evicted_obj.key in entropy_scores:
        del entropy_scores[evicted_obj.key]
    if evicted_obj.key in interactive_scores:
        del interactive_scores[evicted_obj.key]

    # Normalize interactive scores
    total_interactive_score = sum(interactive_scores.values())
    if total_interactive_score > 0:
        for key in interactive_scores:
            interactive_scores[key] /= total_interactive_score