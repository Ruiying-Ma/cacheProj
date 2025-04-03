# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_DECAY = 0.9
TEMPORAL_SKEW_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, which is a combination of access frequency, recency, and a temporal skew factor. It also tracks a decay factor for frequency and a reversal flag that indicates if priority reversal should be applied.
cache_metadata = {
    'frequency': defaultdict(int),
    'priority_score': {},
    'reversal_flag': False,
    'decay_factor': FREQUENCY_DECAY
}

def calculate_priority_score(frequency, recency, skew_factor):
    return frequency * (1 - skew_factor) + recency * skew_factor

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score. If the reversal flag is set, it selects the entry with the highest priority score instead, allowing for adaptive behavior based on workload patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if cache_metadata['reversal_flag']:
        # Select the entry with the highest priority score
        candid_obj_key = max(cache_snapshot.cache.keys(), key=lambda k: cache_metadata['priority_score'][k])
    else:
        # Select the entry with the lowest priority score
        candid_obj_key = min(cache_snapshot.cache.keys(), key=lambda k: cache_metadata['priority_score'][k])
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency of the entry is incremented, and the priority score is recalculated by applying the frequency decay and temporal skew adjustments. The reversal flag is evaluated to determine if a priority reversal is needed.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    cache_metadata['frequency'][obj.key] += 1
    frequency = cache_metadata['frequency'][obj.key]
    recency = cache_snapshot.access_count
    cache_metadata['priority_score'][obj.key] = calculate_priority_score(frequency, recency, TEMPORAL_SKEW_FACTOR)
    
    # Evaluate reversal flag
    if cache_snapshot.hit_count > cache_snapshot.miss_count:
        cache_metadata['reversal_flag'] = True
    else:
        cache_metadata['reversal_flag'] = False

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its initial priority score is calculated based on its temporal skew and a baseline frequency. The reversal flag is checked to ensure the cache adapts to current access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    baseline_frequency = 1
    recency = cache_snapshot.access_count
    cache_metadata['frequency'][obj.key] = baseline_frequency
    cache_metadata['priority_score'][obj.key] = calculate_priority_score(baseline_frequency, recency, TEMPORAL_SKEW_FACTOR)
    
    # Check reversal flag
    if cache_snapshot.hit_count > cache_snapshot.miss_count:
        cache_metadata['reversal_flag'] = True
    else:
        cache_metadata['reversal_flag'] = False

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalibrates the decay factor and evaluates the reversal flag to adaptively adjust to changes in access patterns, ensuring the cache remains responsive to temporal and frequency shifts.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Recalibrate decay factor
    cache_metadata['decay_factor'] *= FREQUENCY_DECAY
    
    # Evaluate reversal flag
    if cache_snapshot.hit_count > cache_snapshot.miss_count:
        cache_metadata['reversal_flag'] = True
    else:
        cache_metadata['reversal_flag'] = False
    
    # Remove metadata for evicted object
    if evicted_obj.key in cache_metadata['frequency']:
        del cache_metadata['frequency'][evicted_obj.key]
    if evicted_obj.key in cache_metadata['priority_score']:
        del cache_metadata['priority_score'][evicted_obj.key]