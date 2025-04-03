# Import anything you need below
import heapq

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a hybrid memory structure that combines a priority queue and a hash map. The priority queue dynamically sorts cache entries based on a composite score of access frequency and recency, while the hash map provides quick access to metadata for each cache entry. Additionally, cache alignment metadata is maintained to optimize data placement for parallel execution.
cache_metadata = {
    'frequency': {},  # Maps object key to access frequency
    'recency': {},    # Maps object key to last access time
    'priority_queue': []  # Min-heap based on composite score
}

def calculate_composite_score(key):
    frequency = cache_metadata['frequency'].get(key, 0)
    recency = cache_metadata['recency'].get(key, 0)
    return FREQUENCY_WEIGHT * frequency + RECENCY_WEIGHT * recency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest composite score in the priority queue. This score is calculated using a weighted sum of access frequency and recency, with weights dynamically adjusted based on current workload characteristics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while cache_metadata['priority_queue']:
        score, key = heapq.heappop(cache_metadata['priority_queue'])
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency counter for the accessed entry in the hash map and updates its recency score. The priority queue is then dynamically re-sorted to reflect the updated composite score, ensuring optimal alignment for parallel execution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_metadata['frequency'][key] = cache_metadata['frequency'].get(key, 0) + 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    score = calculate_composite_score(key)
    heapq.heappush(cache_metadata['priority_queue'], (score, key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency scores in the hash map. The new entry is added to the priority queue, which is then dynamically sorted to maintain optimal cache alignment and prepare for parallel execution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    cache_metadata['frequency'][key] = 1
    cache_metadata['recency'][key] = cache_snapshot.access_count
    score = calculate_composite_score(key)
    heapq.heappush(cache_metadata['priority_queue'], (score, key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the victim's metadata from both the hash map and the priority queue. It then recalibrates the dynamic weights used in the composite score calculation to adapt to the current workload, ensuring efficient cache alignment and parallel execution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in cache_metadata['frequency']:
        del cache_metadata['frequency'][evicted_key]
    if evicted_key in cache_metadata['recency']:
        del cache_metadata['recency'][evicted_key]
    
    # Recalibrate weights (this is a placeholder, as dynamic adjustment logic is not specified)
    # In a real scenario, you might adjust FREQUENCY_WEIGHT and RECENCY_WEIGHT based on workload analysis