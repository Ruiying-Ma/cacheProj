# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_RFA = 1.0
INITIAL_EDC = 0.5
INITIAL_TSF = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Dynamic Allocation Matrix (DAM) to track the frequency and recency of cache accesses, a Resonant Frequency Analysis (RFA) score for each cache entry to measure its access pattern stability, an Entropy Drift Control (EDC) value to monitor the randomness of access patterns, and a Temporal State Fusion (TSF) index to integrate temporal locality with spatial access patterns.
DAM = defaultdict(lambda: {'frequency': 0, 'recency': 0})
RFA = defaultdict(lambda: INITIAL_RFA)
EDC = defaultdict(lambda: INITIAL_EDC)
TSF = defaultdict(lambda: INITIAL_TSF)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score of RFA and TSF, adjusted by the EDC value to prioritize entries with more predictable access patterns. The DAM is used to ensure that the eviction does not disrupt frequently accessed data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (RFA[key] + TSF[key]) * EDC[key]
        if score < min_score and DAM[key]['frequency'] > 0:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the DAM is updated to reflect the increased frequency and recency of the accessed entry. The RFA score is recalculated to account for the new access pattern, while the EDC value is adjusted to reflect any changes in access randomness. The TSF index is updated to integrate the latest temporal access information.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    DAM[key]['frequency'] += 1
    DAM[key]['recency'] = cache_snapshot.access_count
    RFA[key] = 1 / (1 + DAM[key]['frequency'])
    EDC[key] = 1 - (DAM[key]['frequency'] / (DAM[key]['frequency'] + DAM[key]['recency']))
    TSF[key] = cache_snapshot.access_count / (cache_snapshot.access_count + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the DAM is updated to include the new entry with initial frequency and recency values. The RFA score is initialized based on the initial access pattern, while the EDC value is set to a neutral state. The TSF index is initialized to reflect the temporal context of the insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    DAM[key] = {'frequency': 1, 'recency': cache_snapshot.access_count}
    RFA[key] = INITIAL_RFA
    EDC[key] = INITIAL_EDC
    TSF[key] = INITIAL_TSF

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the DAM is adjusted to remove the evicted entry and redistribute its allocation to remaining entries. The RFA scores of remaining entries are recalculated to reflect the new cache state, while the EDC values are updated to account for the change in access pattern predictability. The TSF index is recalibrated to maintain accurate temporal-spatial integration.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in DAM:
        del DAM[evicted_key]
        del RFA[evicted_key]
        del EDC[evicted_key]
        del TSF[evicted_key]
    
    for key in cache_snapshot.cache:
        RFA[key] = 1 / (1 + DAM[key]['frequency'])
        EDC[key] = 1 - (DAM[key]['frequency'] / (DAM[key]['frequency'] + DAM[key]['recency']))
        TSF[key] = cache_snapshot.access_count / (cache_snapshot.access_count + 1)