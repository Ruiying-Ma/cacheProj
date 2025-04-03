# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 1.0
RECENCY_WEIGHT = 1.0
SPATIAL_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-level index structure that tracks both temporal and spatial locality. It includes a frequency counter for each data block, a recency timestamp, and a spatial locality score based on access patterns of neighboring blocks.
frequency_counter = defaultdict(int)
recency_timestamp = {}
spatial_locality_score = defaultdict(float)

def calculate_composite_score(key):
    frequency = frequency_counter[key]
    recency = recency_timestamp[key]
    spatial = spatial_locality_score[key]
    return (FREQUENCY_WEIGHT * frequency) + (RECENCY_WEIGHT * recency) + (SPATIAL_WEIGHT * spatial)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each block, which is a weighted sum of its frequency, recency, and spatial locality score. The block with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the accessed block is incremented, the recency timestamp is updated to the current time, and the spatial locality score is adjusted based on the access patterns of its neighboring blocks.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    frequency_counter[key] += 1
    recency_timestamp[key] = cache_snapshot.access_count
    # Adjust spatial locality score based on neighboring access patterns
    # This is a placeholder for the actual logic
    spatial_locality_score[key] += 0.1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency counter to one, sets the recency timestamp to the current time, and calculates an initial spatial locality score based on the access patterns of its neighboring blocks.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    frequency_counter[key] = 1
    recency_timestamp[key] = cache_snapshot.access_count
    # Calculate initial spatial locality score
    # This is a placeholder for the actual logic
    spatial_locality_score[key] = 0.5

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a block, the policy recalibrates the spatial locality scores of the remaining blocks to reflect the change in neighborhood, ensuring that the scores remain accurate and relevant.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Recalibrate spatial locality scores
    # This is a placeholder for the actual logic
    for key in cache_snapshot.cache:
        spatial_locality_score[key] -= 0.1
    # Clean up metadata for the evicted object
    del frequency_counter[evicted_key]
    del recency_timestamp[evicted_key]
    del spatial_locality_score[evicted_key]