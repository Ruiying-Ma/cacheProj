# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASE_EXECUTION_PROFILE_SCORE = 1.0
REDUNDANCY_WEIGHT = 0.5
ACCESS_FREQUENCY_WEIGHT = 0.3
LAST_ACCESS_TIME_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, redundancy level, and execution profile score for each cache entry. It also tracks a subset of critical data blocks that are frequently accessed together.
metadata = defaultdict(lambda: {
    'access_frequency': 0,
    'last_access_time': 0,
    'redundancy_level': 0,
    'execution_profile_score': BASE_EXECUTION_PROFILE_SCORE
})
critical_subset = set()

def calculate_execution_profile_score(obj_key):
    data = metadata[obj_key]
    return (ACCESS_FREQUENCY_WEIGHT * data['access_frequency'] +
            LAST_ACCESS_TIME_WEIGHT * data['last_access_time'] +
            REDUNDANCY_WEIGHT * data['redundancy_level'])

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying entries with the lowest execution profile score, which is a composite metric derived from access frequency, redundancy level, and last access time. Entries with high redundancy are prioritized for eviction to maintain fault tolerance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = calculate_execution_profile_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and last access time for the entry are updated. The execution profile score is recalculated to reflect the increased likelihood of future access, and the entry's redundancy level is adjusted if it is part of a critical subset.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    obj_key = obj.key
    metadata[obj_key]['access_frequency'] += 1
    metadata[obj_key]['last_access_time'] = cache_snapshot.access_count
    if obj_key in critical_subset:
        metadata[obj_key]['redundancy_level'] += 1
    metadata[obj_key]['execution_profile_score'] = calculate_execution_profile_score(obj_key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline execution profile score, sets its redundancy level based on current cache contents, and updates the subset of critical data blocks if the new entry is frequently accessed with others.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    obj_key = obj.key
    metadata[obj_key] = {
        'access_frequency': 1,
        'last_access_time': cache_snapshot.access_count,
        'redundancy_level': 0,
        'execution_profile_score': BASE_EXECUTION_PROFILE_SCORE
    }
    # Update critical subset if necessary
    if obj_key in critical_subset:
        metadata[obj_key]['redundancy_level'] += 1

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the execution profile scores of remaining entries to account for the change in cache dynamics. It also updates the redundancy levels and critical subset information to ensure continued fault tolerance and subset optimization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in critical_subset:
        critical_subset.remove(evicted_key)
    
    for key in cache_snapshot.cache:
        metadata[key]['execution_profile_score'] = calculate_execution_profile_score(key)
        if key in critical_subset:
            metadata[key]['redundancy_level'] = max(0, metadata[key]['redundancy_level'] - 1)