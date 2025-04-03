# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
LOCALITY_WEIGHT = 0.5
LATENCY_WEIGHT = 0.3
MEMORY_WEIGHT = 0.2
BASELINE_LOCALITY = 1
INITIAL_LATENCY = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-tier metadata structure: a 'locality score' for each cache line based on recent access patterns, a 'latency factor' that estimates the time cost of fetching data from lower cache levels, and a 'memory footprint' indicator that tracks the size and frequency of data usage.
locality_scores = defaultdict(lambda: BASELINE_LOCALITY)
latency_factors = defaultdict(lambda: INITIAL_LATENCY)
memory_footprints = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by calculating a composite score for each cache line, which is a weighted sum of the inverse of the locality score, the latency factor, and the memory footprint. The line with the lowest composite score is chosen for eviction, prioritizing lines with low locality, high latency, and large memory footprint.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        locality_score = locality_scores[key]
        latency_factor = latency_factors[key]
        memory_footprint = memory_footprints[key]
        
        composite_score = (LOCALITY_WEIGHT / locality_score) + \
                          (LATENCY_WEIGHT * latency_factor) + \
                          (MEMORY_WEIGHT * memory_footprint)
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the locality score of the accessed line is incremented to reflect increased data locality. The latency factor is adjusted based on the current cache level's performance metrics, and the memory footprint is updated to account for the frequency of access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    locality_scores[obj.key] += 1
    latency_factors[obj.key] = max(1, latency_factors[obj.key] - 1)
    memory_footprints[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the locality score is initialized to a baseline value, the latency factor is set based on the expected cost of accessing this data from lower cache levels, and the memory footprint is estimated based on the object's size and initial access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    locality_scores[obj.key] = BASELINE_LOCALITY
    latency_factors[obj.key] = INITIAL_LATENCY
    memory_footprints[obj.key] = obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the locality scores of remaining lines to ensure they reflect the current access patterns, adjusts the latency factors to account for the change in cache composition, and updates the memory footprint indicators to redistribute the freed space's impact on cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in locality_scores:
        del locality_scores[evicted_obj.key]
    if evicted_obj.key in latency_factors:
        del latency_factors[evicted_obj.key]
    if evicted_obj.key in memory_footprints:
        del memory_footprints[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        locality_scores[key] = max(BASELINE_LOCALITY, locality_scores[key] - 1)
        latency_factors[key] = min(INITIAL_LATENCY, latency_factors[key] + 1)
        memory_footprints[key] = max(1, memory_footprints[key] - 1)