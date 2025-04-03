# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-layered metadata structure including access frequency, recency, and a dynamic load factor for each cache entry. It also tracks a global cache load index to optimize parallel processing and resilience.
access_frequency = defaultdict(lambda: BASELINE_FREQUENCY)
recency = defaultdict(lambda: BASELINE_RECENCY)
load_factor = defaultdict(float)
global_cache_load_index = 0.0

def calculate_composite_score(key):
    # Calculate the composite score for eviction
    freq = access_frequency[key]
    rec = recency[key]
    load = load_factor[key]
    return 1 / (freq * rec * load)

def recalculate_global_cache_load_index(cache_snapshot):
    # Recalculate the global cache load index
    total_load = sum(load_factor.values())
    global global_cache_load_index
    global_cache_load_index = total_load / len(cache_snapshot.cache) if cache_snapshot.cache else 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on a composite score derived from the inverse of access frequency, recency, and the load factor. Entries with the lowest scores are prioritized for eviction, ensuring balanced load distribution and resilience.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are incremented. The global cache load index is recalculated to reflect the updated state, ensuring optimal load distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] += 1
    recency[obj.key] += 1
    recalculate_global_cache_load_index(cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency to baseline values and updates the global cache load index to account for the new entry, maintaining balance across the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] = BASELINE_FREQUENCY
    recency[obj.key] = BASELINE_RECENCY
    load_factor[obj.key] = 1.0  # Initialize load factor
    recalculate_global_cache_load_index(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the global cache load index and adjusts the load factors of remaining entries to ensure continued optimal load distribution and resilience.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del access_frequency[evicted_obj.key]
    del recency[evicted_obj.key]
    del load_factor[evicted_obj.key]
    recalculate_global_cache_load_index(cache_snapshot)
    # Adjust load factors of remaining entries
    for key in cache_snapshot.cache:
        load_factor[key] = (access_frequency[key] + recency[key]) / 2.0