# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_COHERENCY_SCORE = 1
DEPENDENCY_INCREMENT = 1
COHERENCY_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic partitioning table that divides the cache into segments based on access patterns, an adaptive coherency score for each cache line to track data consistency needs, a priority elimination list to identify low-priority data, and a synchronization matrix to manage dependencies between cache lines.
dynamic_partitioning_table = defaultdict(int)
adaptive_coherency_scores = defaultdict(lambda: INITIAL_COHERENCY_SCORE)
priority_elimination_list = []
synchronization_matrix = defaultdict(lambda: defaultdict(int))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first consulting the priority elimination list to remove low-priority data, then checking the adaptive coherency scores to ensure minimal impact on data consistency, and finally using the synchronization matrix to avoid evicting lines with high dependency scores.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Step 1: Check the priority elimination list
    for key in priority_elimination_list:
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break

    # Step 2: Check adaptive coherency scores
    if not candid_obj_key:
        min_coherency_score = float('inf')
        for key, cached_obj in cache_snapshot.cache.items():
            if adaptive_coherency_scores[key] < min_coherency_score:
                min_coherency_score = adaptive_coherency_scores[key]
                candid_obj_key = key

    # Step 3: Check synchronization matrix
    if candid_obj_key:
        min_dependency_score = float('inf')
        for key, cached_obj in cache_snapshot.cache.items():
            dependency_score = sum(synchronization_matrix[key].values())
            if dependency_score < min_dependency_score:
                min_dependency_score = dependency_score
                candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the dynamic partitioning table is adjusted to reflect the increased access frequency, the adaptive coherency score is incremented to indicate higher consistency needs, and the synchronization matrix is updated to strengthen dependencies with frequently accessed lines.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    dynamic_partitioning_table[obj.key] += 1
    adaptive_coherency_scores[obj.key] += COHERENCY_INCREMENT
    for key in cache_snapshot.cache:
        if key != obj.key:
            synchronization_matrix[obj.key][key] += DEPENDENCY_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the dynamic partitioning table is updated to accommodate the new access pattern, the adaptive coherency score is initialized based on initial access predictions, and the synchronization matrix is adjusted to include potential dependencies with existing cache lines.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    dynamic_partitioning_table[obj.key] = 1
    adaptive_coherency_scores[obj.key] = INITIAL_COHERENCY_SCORE
    for key in cache_snapshot.cache:
        if key != obj.key:
            synchronization_matrix[obj.key][key] = DEPENDENCY_INCREMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the dynamic partitioning table is recalibrated to reflect the removal, the adaptive coherency scores of remaining lines are adjusted to redistribute consistency priorities, and the synchronization matrix is updated to remove dependencies related to the evicted line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in dynamic_partitioning_table:
        del dynamic_partitioning_table[evicted_obj.key]
    if evicted_obj.key in adaptive_coherency_scores:
        del adaptive_coherency_scores[evicted_obj.key]
    if evicted_obj.key in synchronization_matrix:
        del synchronization_matrix[evicted_obj.key]
    for key in synchronization_matrix:
        if evicted_obj.key in synchronization_matrix[key]:
            del synchronization_matrix[key][evicted_obj.key]