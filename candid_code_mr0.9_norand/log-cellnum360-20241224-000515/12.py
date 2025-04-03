# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_INCREMENT = 10
DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each page, which is a combination of access frequency, recency, and a decay factor that reduces the score over time. It also tracks the memory footprint of each page to optimize space usage.
priority_scores = defaultdict(lambda: 0)
last_access_time = defaultdict(lambda: 0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the page with the lowest priority score for eviction, ensuring that pages with low access frequency and recency are removed first. It also considers the memory footprint, preferring to evict larger pages if scores are similar, to optimize space.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        # Calculate effective priority score considering decay
        effective_priority = priority_scores[key] * (DECAY_FACTOR ** (cache_snapshot.access_count - last_access_time[key]))
        
        # Choose the object with the lowest effective priority score
        if effective_priority < min_priority_score or (effective_priority == min_priority_score and cached_obj.size > cache_snapshot.cache[candid_obj_key].size):
            min_priority_score = effective_priority
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority score of the accessed page by a fixed increment and resets its decay timer, ensuring that frequently accessed pages remain in the cache longer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    priority_scores[obj.key] += PRIORITY_INCREMENT
    last_access_time[obj.key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score based on its initial access frequency and memory footprint, and starts its decay timer to ensure it can be fairly compared with existing pages.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    priority_scores[obj.key] = obj.size
    last_access_time[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the decay factor for remaining pages to ensure that their priority scores reflect the current access patterns and memory constraints, maintaining an adaptive balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate decay factors for remaining pages
    for key in cache_snapshot.cache:
        priority_scores[key] *= (DECAY_FACTOR ** (cache_snapshot.access_count - last_access_time[key]))
        last_access_time[key] = cache_snapshot.access_count