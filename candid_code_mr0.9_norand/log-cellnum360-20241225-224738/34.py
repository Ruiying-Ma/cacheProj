# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
SIZE_WEIGHT = 1.0
COMPRESSION_BENEFIT_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data size, and a compression benefit score for each cache entry. It also tracks overall cache miss penalty statistics to adaptively adjust eviction priorities.
metadata = {
    'access_frequency': defaultdict(int),
    'last_access_time': {},
    'compression_benefit': defaultdict(float),
    'miss_penalty': 0.0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which considers the access frequency, recency, data size, and compression benefit. Entries with lower scores are prioritized for eviction, with adjustments made based on current cache miss penalty trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['access_frequency'][key]
        recency = cache_snapshot.access_count - metadata['last_access_time'][key]
        size = cached_obj.size
        compression_benefit = metadata['compression_benefit'][key]
        
        score = (FREQUENCY_WEIGHT * frequency +
                 RECENCY_WEIGHT * recency +
                 SIZE_WEIGHT * size +
                 COMPRESSION_BENEFIT_WEIGHT * compression_benefit)
        
        # Adjust score based on miss penalty
        score += metadata['miss_penalty']
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time for the accessed entry. It also recalculates the compression benefit score to reflect any changes in data access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    
    # Recalculate compression benefit score (dummy calculation for example)
    metadata['compression_benefit'][key] = 1.0 / (1 + metadata['access_frequency'][key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with default values and updates the overall cache miss penalty statistics to reflect the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['last_access_time'][key] = cache_snapshot.access_count
    metadata['compression_benefit'][key] = 1.0  # Initial compression benefit score
    
    # Update miss penalty (dummy calculation for example)
    metadata['miss_penalty'] = cache_snapshot.miss_count / (cache_snapshot.access_count + 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the composite scores of remaining entries, taking into account the updated cache miss penalty statistics, and adjusts the compression benefit scores to optimize for latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalculate miss penalty (dummy calculation for example)
    metadata['miss_penalty'] = cache_snapshot.miss_count / (cache_snapshot.access_count + 1)
    
    # Adjust compression benefit scores for remaining entries
    for key in cache_snapshot.cache:
        metadata['compression_benefit'][key] *= 0.9  # Example adjustment