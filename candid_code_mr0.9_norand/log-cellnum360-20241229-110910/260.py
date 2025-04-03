# Import anything you need below
import math
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_ENTROPY = 1.0
MODULATION_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal access pattern history for each cache entry, an entropy score representing the unpredictability of access patterns, and a modulation factor that adjusts based on recent access trends.
temporal_access_history = defaultdict(list)
entropy_scores = defaultdict(lambda: BASELINE_ENTROPY)
modulation_factors = defaultdict(lambda: MODULATION_FACTOR)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim by identifying entries with the highest entropic divergence, indicating unpredictable access patterns, and applies reactive modulation to prioritize entries with less recent access, considering temporal loopback to avoid evicting entries likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_divergence = -math.inf

    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate entropic divergence
        entropy = entropy_scores[key]
        modulation = modulation_factors[key]
        last_access_time = temporal_access_history[key][-1] if temporal_access_history[key] else 0
        divergence = entropy + modulation * (cache_snapshot.access_count - last_access_time)

        # Select the object with the highest divergence
        if divergence > max_divergence:
            max_divergence = divergence
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal access pattern is updated to reflect the current time, the entropy score is recalculated to account for the new access, and the modulation factor is adjusted to reflect the increased likelihood of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_access_history[key].append(cache_snapshot.access_count)

    # Recalculate entropy score
    if len(temporal_access_history[key]) > 1:
        intervals = [t2 - t1 for t1, t2 in zip(temporal_access_history[key], temporal_access_history[key][1:])]
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            entropy_scores[key] = -sum((i / avg_interval) * math.log(i / avg_interval) for i in intervals if i > 0)

    # Adjust modulation factor
    modulation_factors[key] *= (1 + MODULATION_FACTOR)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal access pattern is initialized, the entropy score is set to a baseline value, and the modulation factor is adjusted to reflect the initial uncertainty of future accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_access_history[key] = [cache_snapshot.access_count]
    entropy_scores[key] = BASELINE_ENTROPY
    modulation_factors[key] = MODULATION_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the entropy scores of remaining entries to reflect the reduced cache size, adjusts the modulation factors to account for the change in cache dynamics, and updates temporal patterns to ensure loopback considerations are current.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_access_history:
        del temporal_access_history[evicted_key]
        del entropy_scores[evicted_key]
        del modulation_factors[evicted_key]

    # Recalibrate entropy scores and modulation factors for remaining entries
    for key in cache_snapshot.cache:
        modulation_factors[key] *= (1 - MODULATION_FACTOR)
        # Update temporal patterns to ensure loopback considerations
        if temporal_access_history[key]:
            last_access_time = temporal_access_history[key][-1]
            if cache_snapshot.access_count - last_access_time > cache_snapshot.capacity:
                temporal_access_history[key].append(cache_snapshot.access_count)