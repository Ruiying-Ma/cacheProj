# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a linear hash table for cache entries, a frequency hash table to track access frequency, and a conflict resolution table to manage page conflicts. It also tracks page migration history to optimize future placements.
frequency_table = defaultdict(int)  # Tracks access frequency of each object
conflict_table = defaultdict(int)  # Tracks conflict rate of each object
migration_history = deque()  # Tracks the order of page migrations

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the least frequently accessed page using the frequency hash table. In case of a tie, it uses the conflict resolution table to select the page with the highest conflict rate. If conflicts are also tied, it considers the page migration history to evict the page with the least recent migration.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_frequency = float('inf')
    candidates = []

    # Find the least frequently accessed pages
    for key, cached_obj in cache_snapshot.cache.items():
        freq = frequency_table[key]
        if freq < min_frequency:
            min_frequency = freq
            candidates = [key]
        elif freq == min_frequency:
            candidates.append(key)

    # If there's a tie, use the conflict resolution table
    if len(candidates) > 1:
        max_conflict = -1
        conflict_candidates = []
        for key in candidates:
            conflict = conflict_table[key]
            if conflict > max_conflict:
                max_conflict = conflict
                conflict_candidates = [key]
            elif conflict == max_conflict:
                conflict_candidates.append(key)
        candidates = conflict_candidates

    # If there's still a tie, use the migration history
    if len(candidates) > 1:
        for key in migration_history:
            if key in candidates:
                candid_obj_key = key
                break
    else:
        candid_obj_key = candidates[0]

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency in the frequency hash table and updates the conflict resolution table to reflect reduced conflict likelihood. It also logs the access in the page migration history to track recent activity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    frequency_table[obj.key] += 1
    conflict_table[obj.key] = max(0, conflict_table[obj.key] - 1)
    if obj.key in migration_history:
        migration_history.remove(obj.key)
    migration_history.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency count in the frequency hash table, updates the conflict resolution table to account for potential new conflicts, and logs the insertion in the page migration history to track its initial placement.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    frequency_table[obj.key] = 1
    conflict_table[obj.key] += 1
    migration_history.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted page's entry from the linear hash table, decrements its frequency count in the frequency hash table, updates the conflict resolution table to reflect reduced conflicts, and logs the eviction in the page migration history to inform future decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in frequency_table:
        del frequency_table[evicted_obj.key]
    if evicted_obj.key in conflict_table:
        del conflict_table[evicted_obj.key]
    if evicted_obj.key in migration_history:
        migration_history.remove(evicted_obj.key)