# Import anything you need below
import math

# Put tunable constant parameters below
BASELINE_TD = 10
DEFAULT_PVM = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Pattern Matrix (QPM) to track access patterns, a Temporal Differential (TD) to measure time between accesses, an Entropic Transfer Map (ETM) to assess data entropy, and a Predictive Vector Model (PVM) to forecast future access likelihood.
QPM = {}
TD = {}
ETM = {}
PVM = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score from the QPM, TD, ETM, and PVM, prioritizing entries with low access patterns, high temporal differentials, high entropy, and low predicted future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        qpm_score = QPM.get(key, 0)
        td_score = TD.get(key, BASELINE_TD)
        etm_score = ETM.get(key, 0)
        pvm_score = PVM.get(key, DEFAULT_PVM)
        
        combined_score = qpm_score + td_score + etm_score - pvm_score
        
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QPM is updated to reinforce the current access pattern, the TD is reset to zero for the accessed entry, the ETM is adjusted to reflect reduced entropy, and the PVM is recalibrated to increase the likelihood of future access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    QPM[key] = QPM.get(key, 0) + 1
    TD[key] = 0
    ETM[key] = max(0, ETM.get(key, 0) - 1)
    PVM[key] = min(1, PVM.get(key, DEFAULT_PVM) + 0.1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QPM is initialized with a neutral pattern, the TD is set to a baseline value, the ETM is calculated based on initial data entropy, and the PVM is initialized with a default prediction of future access likelihood.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    QPM[key] = 0
    TD[key] = BASELINE_TD
    ETM[key] = math.log(obj.size + 1)
    PVM[key] = DEFAULT_PVM

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QPM is adjusted to remove the evicted pattern, the TD is recalibrated for remaining entries, the ETM is updated to reflect the change in overall cache entropy, and the PVM is recalculated to adjust predictions based on the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in QPM:
        del QPM[evicted_key]
    if evicted_key in TD:
        del TD[evicted_key]
    if evicted_key in ETM:
        del ETM[evicted_key]
    if evicted_key in PVM:
        del PVM[evicted_key]
    
    for key in cache_snapshot.cache:
        TD[key] += 1
        ETM[key] = math.log(cache_snapshot.cache[key].size + 1)
        PVM[key] = max(0, PVM[key] - 0.05)