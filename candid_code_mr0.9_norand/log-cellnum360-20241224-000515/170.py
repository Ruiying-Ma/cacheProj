# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_INCREMENT = 10
INITIAL_PRIORITY = 50
IMPORTANCE_LEVEL = 1  # User-defined importance level

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a dynamic cache size factor, and an intrinsic order index. The priority score is calculated based on access frequency, recency, and a user-defined importance level. The dynamic cache size factor adjusts the cache size based on system load and available resources. The intrinsic order index helps in sorting entries for efficient access and eviction decisions.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY)
intrinsic_order_indices = {}
dynamic_cache_size_factor = 1.0
current_order_index = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score. In case of a tie, it uses the intrinsic order index to break the tie, evicting the entry with the lowest index. This ensures that less important and less frequently accessed items are evicted first, while maintaining efficient cache operations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    min_index = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_scores[key]
        index = intrinsic_order_indices[key]
        
        if priority < min_priority or (priority == min_priority and index < min_index):
            min_priority = priority
            min_index = index
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority score of the accessed entry by a predefined increment, reflecting its increased importance. The intrinsic order index of the entry is updated to reflect its new position in the access order, ensuring efficient sorting for future operations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] += PRIORITY_INCREMENT
    global current_order_index
    current_order_index += 1
    intrinsic_order_indices[obj.key] = current_order_index

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on its user-defined importance and sets its intrinsic order index to the highest current value, indicating it as the most recently accessed. The dynamic cache size factor is recalculated to ensure optimal resource utilization.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority_scores[obj.key] = INITIAL_PRIORITY * IMPORTANCE_LEVEL
    global current_order_index
    current_order_index += 1
    intrinsic_order_indices[obj.key] = current_order_index
    recalculate_dynamic_cache_size_factor(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic cache size factor to reflect the current system load and available resources. It also adjusts the intrinsic order indices of remaining entries to maintain a consistent and efficient order for future access and eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del priority_scores[evicted_obj.key]
    del intrinsic_order_indices[evicted_obj.key]
    recalculate_dynamic_cache_size_factor(cache_snapshot)

def recalculate_dynamic_cache_size_factor(cache_snapshot):
    '''
    Recalculates the dynamic cache size factor based on current system load and available resources.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
    - Return: `None`
    '''
    global dynamic_cache_size_factor
    dynamic_cache_size_factor = cache_snapshot.size / cache_snapshot.capacity