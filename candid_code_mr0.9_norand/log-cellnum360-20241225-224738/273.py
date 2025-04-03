# Import anything you need below
from collections import defaultdict
import heapq

# Put tunable constant parameters below
INITIAL_PRIORITY = 1
PRIORITY_INCREMENT = 1
PD_INITIAL_SCORE = 1.0
PD_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains an Adaptive Quantum Layer (AQL) that dynamically adjusts the priority of cache entries based on access patterns. It also tracks a Predictive Drift (PD) score for each entry, estimating future access likelihood. A Temporal Cascade (TC) records the recency and frequency of accesses, while a Dynamic Allocation Index (DAI) allocates cache space adaptively based on current workload characteristics.
AQL = defaultdict(lambda: INITIAL_PRIORITY)
PD = defaultdict(lambda: PD_INITIAL_SCORE)
TC = {}
DAI = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by combining the Predictive Drift score and the Temporal Cascade data. Entries with the lowest PD score and least recent access in the TC are prioritized for eviction, ensuring that less likely to be accessed items are removed first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_pd_score = float('inf')
    oldest_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        pd_score = PD[key]
        last_access_time = TC.get(key, float('inf'))
        
        if pd_score < min_pd_score or (pd_score == min_pd_score and last_access_time < oldest_time):
            min_pd_score = pd_score
            oldest_time = last_access_time
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Adaptive Quantum Layer increases the priority of the accessed entry, while the Predictive Drift score is recalibrated to reflect the increased likelihood of future access. The Temporal Cascade is updated to record the recent access, and the Dynamic Allocation Index is adjusted if the hit pattern suggests a shift in workload.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    AQL[obj.key] += PRIORITY_INCREMENT
    PD[obj.key] *= PD_DECAY_FACTOR
    TC[obj.key] = cache_snapshot.access_count
    # Adjust DAI if needed (not implemented due to lack of specific workload pattern data)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Adaptive Quantum Layer assigns an initial priority based on the current workload. The Predictive Drift score is initialized using historical access patterns if available. The Temporal Cascade records the insertion time, and the Dynamic Allocation Index is updated to reflect the new cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    AQL[obj.key] = INITIAL_PRIORITY
    PD[obj.key] = PD_INITIAL_SCORE
    TC[obj.key] = cache_snapshot.access_count
    # Update DAI to reflect new cache composition (not implemented due to lack of specific workload pattern data)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Adaptive Quantum Layer recalibrates priorities of remaining entries to maintain balance. The Predictive Drift scores of remaining entries are adjusted to account for the removal. The Temporal Cascade is updated to remove the evicted entry's data, and the Dynamic Allocation Index is recalculated to optimize space for future entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del AQL[evicted_obj.key]
    del PD[evicted_obj.key]
    del TC[evicted_obj.key]
    # Recalculate DAI to optimize space (not implemented due to lack of specific workload pattern data)