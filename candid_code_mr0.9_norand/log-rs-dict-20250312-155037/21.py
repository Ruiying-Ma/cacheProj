# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
INITIAL_LUTEINIZING_SCORE = 1000

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a unique identifier for each cache entry. Additionally, it tracks a 'luteinizing' score which is a composite metric derived from access patterns and system load.
metadata = {
    'access_frequency': {},
    'recency_of_access': {},
    'luteinizing_score': {}
}

def calculate_luteinizing_score(access_frequency, recency_of_access, current_time):
    # Example calculation for luteinizing score
    return access_frequency * math.log(current_time - recency_of_access + 1)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest luteinizing score. If multiple entries have the same score, it evicts the least recently accessed entry among them.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    min_recency = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata['luteinizing_score'][key]
        recency = metadata['recency_of_access'][key]
        
        if score < min_score or (score == min_score and recency < min_recency):
            min_score = score
            min_recency = recency
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and recency of access for the hit entry are updated. The luteinizing score is recalculated to reflect the increased access frequency and recency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency_of_access'][key] = cache_snapshot.access_count
    metadata['luteinizing_score'][key] = calculate_luteinizing_score(
        metadata['access_frequency'][key],
        metadata['recency_of_access'][key],
        cache_snapshot.access_count
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial luteinizing score based on system load and expected access patterns. The access frequency is set to 1, and the recency of access is marked as the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency_of_access'][key] = cache_snapshot.access_count
    metadata['luteinizing_score'][key] = INITIAL_LUTEINIZING_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the luteinizing scores for remaining entries to ensure they reflect the current system load and access patterns. It also updates the access frequency and recency metadata to maintain consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['recency_of_access'][evicted_key]
    del metadata['luteinizing_score'][evicted_key]
    
    for key in cache_snapshot.cache.keys():
        metadata['luteinizing_score'][key] = calculate_luteinizing_score(
            metadata['access_frequency'][key],
            metadata['recency_of_access'][key],
            cache_snapshot.access_count
        )