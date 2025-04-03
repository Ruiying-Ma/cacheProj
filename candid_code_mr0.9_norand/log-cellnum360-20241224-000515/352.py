# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_RESILIENCE_SCORE = 1
HEURISTIC_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a resilience score for each cache entry, a streamlined access frequency counter, a heuristic map of access patterns, and a synchronization timestamp for each entry.
access_frequency = defaultdict(int)
heuristic_map = defaultdict(float)
synchronization_timestamp = defaultdict(int)
resilience_score = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest resilience score, which is calculated using a combination of low access frequency, unfavorable heuristic mapping, and outdated synchronization timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_resilience_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (access_frequency[key] * heuristic_map[key]) / (cache_snapshot.access_count - synchronization_timestamp[key] + 1)
        resilience_score[key] = score
        if score < min_resilience_score:
            min_resilience_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the resilience score is increased by incrementing the access frequency counter, updating the heuristic map to reflect recent access patterns, and refreshing the synchronization timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    heuristic_map[key] = heuristic_map[key] * HEURISTIC_DECAY_FACTOR + 1
    synchronization_timestamp[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the resilience score with a baseline value, sets the access frequency counter to one, maps the initial access pattern heuristically, and records the current time as the synchronization timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    heuristic_map[key] = 1.0
    synchronization_timestamp[key] = cache_snapshot.access_count
    resilience_score[key] = BASELINE_RESILIENCE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the heuristic map to deprioritize the evicted pattern, adjusts the resilience scores of remaining entries to reflect the new cache state, and updates synchronization timestamps to ensure optimized synchronization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    heuristic_map[evicted_key] *= HEURISTIC_DECAY_FACTOR
    
    for key in cache_snapshot.cache:
        resilience_score[key] = (access_frequency[key] * heuristic_map[key]) / (cache_snapshot.access_count - synchronization_timestamp[key] + 1)
        synchronization_timestamp[key] = cache_snapshot.access_count