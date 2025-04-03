# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_UTILIZATION_SCORE = 1
INITIAL_LATENCY_REQUIREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a Predictive Utilization Matrix (PUM) that records access patterns and latency requirements for different data segments. It also tracks sequential access indicators and contextual data segments to understand the nature of data access.
PUM = defaultdict(lambda: {'utilization_score': INITIAL_UTILIZATION_SCORE, 'latency_requirement': INITIAL_LATENCY_REQUIREMENT, 'sequential_access': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by analyzing the PUM to identify data segments with the lowest predicted future utilization and highest latency tolerance, while also considering sequential access patterns to avoid disrupting ongoing sequences.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        pum_entry = PUM[key]
        score = pum_entry['utilization_score'] - pum_entry['latency_requirement'] + pum_entry['sequential_access']
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the PUM by increasing the predicted utilization score for the accessed data segment and adjusting the latency requirement based on the current access context. Sequential access indicators are also updated to reflect continued access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    pum_entry = PUM[obj.key]
    pum_entry['utilization_score'] += 1
    pum_entry['latency_requirement'] = max(1, pum_entry['latency_requirement'] - 1)
    pum_entry['sequential_access'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy updates the PUM by initializing the predicted utilization score and latency requirement based on the initial access context. It also updates the contextual data segmentation to include the new object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    PUM[obj.key] = {
        'utilization_score': INITIAL_UTILIZATION_SCORE,
        'latency_requirement': INITIAL_LATENCY_REQUIREMENT,
        'sequential_access': 0
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the PUM by removing the evicted data segment's entry and recalibrating the predicted utilization scores and latency requirements for remaining segments. Sequential access indicators are adjusted to account for the removal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in PUM:
        del PUM[evicted_obj.key]
    
    for key in PUM:
        PUM[key]['utilization_score'] = max(1, PUM[key]['utilization_score'] - 1)
        PUM[key]['latency_requirement'] += 1
        PUM[key]['sequential_access'] = max(0, PUM[key]['sequential_access'] - 1)