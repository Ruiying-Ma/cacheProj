# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
INITIAL_PREDICTIVE_RESONANCE = 1.0
ENTROPY_INFLUENCE_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a Temporal Matrix to track access patterns over time, a Predictive Resonance score for each cache entry to estimate future access likelihood, and an Entropy Influence metric to measure the variability of access patterns. Dynamic Calibration adjusts the weight of these factors based on recent cache performance.
temporal_matrix = defaultdict(list)  # Maps object keys to a list of access times
predictive_resonance = defaultdict(lambda: INITIAL_PREDICTIVE_RESONANCE)  # Maps object keys to their predictive resonance scores
entropy_influence = defaultdict(float)  # Maps object keys to their entropy influence

def calculate_entropy_influence(key):
    # Calculate entropy influence based on access patterns
    access_times = temporal_matrix[key]
    if len(access_times) < 2:
        return 0.0
    intervals = [access_times[i] - access_times[i - 1] for i in range(1, len(access_times))]
    mean_interval = sum(intervals) / len(intervals)
    variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
    return math.sqrt(variance)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest Predictive Resonance score, adjusted by the Entropy Influence to account for unpredictable access patterns. Dynamic Calibration ensures that the selection process adapts to changing workload characteristics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = predictive_resonance[key] - ENTROPY_INFLUENCE_WEIGHT * entropy_influence[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Temporal Matrix is updated to reflect the latest access time, the Predictive Resonance score is increased to indicate higher future access probability, and the Entropy Influence is recalculated to capture any changes in access variability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_matrix[key].append(cache_snapshot.access_count)
    predictive_resonance[key] += 1
    entropy_influence[key] = calculate_entropy_influence(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Temporal Matrix is initialized with the current access time, the Predictive Resonance score is set based on initial access frequency predictions, and the Entropy Influence is adjusted to incorporate the new entry's impact on overall access variability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_matrix[key] = [cache_snapshot.access_count]
    predictive_resonance[key] = INITIAL_PREDICTIVE_RESONANCE
    entropy_influence[key] = calculate_entropy_influence(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Temporal Matrix is purged of the evicted entry's data, the Predictive Resonance scores of remaining entries are recalibrated to reflect the updated cache state, and the Entropy Influence is recalculated to account for the removal of the evicted entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_matrix:
        del temporal_matrix[evicted_key]
    if evicted_key in predictive_resonance:
        del predictive_resonance[evicted_key]
    if evicted_key in entropy_influence:
        del entropy_influence[evicted_key]
    
    # Recalculate entropy influence for all remaining entries
    for key in cache_snapshot.cache:
        entropy_influence[key] = calculate_entropy_influence(key)