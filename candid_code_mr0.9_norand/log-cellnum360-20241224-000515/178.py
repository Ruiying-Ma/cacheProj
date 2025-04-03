# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
PREDICTIVE_LOAD_INCREMENT = 0.1
DEFAULT_PRIORITY_LEVEL = 1
ADAPTIVE_RESOURCE_FACTOR_BASE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic queue for each cache entry, a predictive load score, a priority level, and an adaptive resource allocation factor. The dynamic queue tracks recent access patterns, the predictive load score estimates future access likelihood, the priority level indicates the importance of the entry, and the adaptive resource allocation factor adjusts based on system load.
dynamic_queues = defaultdict(deque)
predictive_load_scores = defaultdict(lambda: 0.0)
priority_levels = defaultdict(lambda: DEFAULT_PRIORITY_LEVEL)
adaptive_resource_allocation_factor = ADAPTIVE_RESOURCE_FACTOR_BASE

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined score of predictive load and priority level, adjusted by the adaptive resource allocation factor. This ensures that less important and less likely to be accessed entries are evicted first, while considering current system load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = (predictive_load_scores[key] + priority_levels[key]) * adaptive_resource_allocation_factor
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the dynamic queue for the accessed entry is updated to reflect the recent access, the predictive load score is increased slightly, and the priority level is re-evaluated based on the frequency of access. The adaptive resource allocation factor is adjusted to reflect the current system load and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    dynamic_queues[key].append(cache_snapshot.access_count)
    predictive_load_scores[key] += PREDICTIVE_LOAD_INCREMENT
    priority_levels[key] = len(dynamic_queues[key])
    adaptive_resource_allocation_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the dynamic queue is initialized with the current access, the predictive load score is set based on initial access patterns, and a default priority level is assigned. The adaptive resource allocation factor is recalibrated to account for the new entry and its potential impact on system resources.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    dynamic_queues[key] = deque([cache_snapshot.access_count])
    predictive_load_scores[key] = PREDICTIVE_LOAD_INCREMENT
    priority_levels[key] = DEFAULT_PRIORITY_LEVEL
    adaptive_resource_allocation_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the dynamic queues of remaining entries are adjusted to reflect the change in cache composition, the predictive load scores are recalculated to account for the freed resources, and priority levels are re-assessed. The adaptive resource allocation factor is updated to optimize resource distribution post-eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in dynamic_queues:
        del dynamic_queues[evicted_key]
        del predictive_load_scores[evicted_key]
        del priority_levels[evicted_key]
    
    for key in cache_snapshot.cache:
        priority_levels[key] = len(dynamic_queues[key])
    
    adaptive_resource_allocation_factor = cache_snapshot.size / cache_snapshot.capacity