# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
NEUTRAL_NEE_SCORE = 0.5
BASELINE_ACL_COUNTER = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Displacement Map (QDM) for each cache line, a Neural Entropy Equilibrium (NEE) score, a Temporal Shift Controller (TSC) timestamp, and an Adaptive Cycle Logic (ACL) counter.
QDM = defaultdict(lambda: 0)
NEE = defaultdict(lambda: NEUTRAL_NEE_SCORE)
TSC = defaultdict(lambda: 0)
ACL = defaultdict(lambda: BASELINE_ACL_COUNTER)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the highest NEE score, indicating the least equilibrium, and the oldest TSC timestamp, suggesting it is the least recently used. The ACL counter is used to break ties by selecting the line with the lowest counter value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    max_nee = -1
    oldest_tsc = float('inf')
    min_acl = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if (NEE[key] > max_nee or
            (NEE[key] == max_nee and TSC[key] < oldest_tsc) or
            (NEE[key] == max_nee and TSC[key] == oldest_tsc and ACL[key] < min_acl)):
            max_nee = NEE[key]
            oldest_tsc = TSC[key]
            min_acl = ACL[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QDM is adjusted to reflect the new access pattern, the NEE score is recalibrated to lower entropy, the TSC timestamp is updated to the current time, and the ACL counter is incremented to reflect increased usage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    QDM[obj.key] += 1
    NEE[obj.key] = max(0, NEE[obj.key] - 0.1)  # Example recalibration
    TSC[obj.key] = cache_snapshot.access_count
    ACL[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QDM is initialized based on initial access patterns, the NEE score is set to a neutral value, the TSC timestamp is set to the current time, and the ACL counter is initialized to a baseline value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    QDM[obj.key] = 1
    NEE[obj.key] = NEUTRAL_NEE_SCORE
    TSC[obj.key] = cache_snapshot.access_count
    ACL[obj.key] = BASELINE_ACL_COUNTER

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QDM is recalibrated to account for the removed line, the NEE scores of remaining lines are adjusted to reflect the new equilibrium, the TSC timestamps are shifted to maintain relative order, and the ACL counters are decremented to balance the cycle logic.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del QDM[evicted_obj.key]
    del NEE[evicted_obj.key]
    del TSC[evicted_obj.key]
    del ACL[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        NEE[key] = min(1, NEE[key] + 0.05)  # Example adjustment
        TSC[key] += 1
        ACL[key] = max(0, ACL[key] - 1)