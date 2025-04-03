# Import anything you need below
import heapq
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1.0
PRIORITY_INCREMENT = 1.0
RECALIBRATION_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue where each cache entry is assigned a priority score based on temporal access patterns and adaptive indexing. It also tracks a temporal index for each entry to sort them based on recent access times.
priority_queue = []  # Min-heap based on (priority_score, temporal_index, obj_key)
priority_scores = defaultdict(lambda: INITIAL_PRIORITY_SCORE)
temporal_indices = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score from the priority queue. If there are ties, it uses the temporal index to evict the least recently accessed entry among those with the lowest score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        priority_score, temporal_index, obj_key = heapq.heappop(priority_queue)
        if obj_key in cache_snapshot.cache:
            candid_obj_key = obj_key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority score of the accessed entry and updates its temporal index to reflect the current time, ensuring it moves up in the priority queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    priority_scores[obj_key] += PRIORITY_INCREMENT
    temporal_indices[obj_key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (priority_scores[obj_key], temporal_indices[obj_key], obj_key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it an initial priority score based on its expected access frequency and updates its temporal index to the current time, placing it appropriately in the priority queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    priority_scores[obj_key] = INITIAL_PRIORITY_SCORE
    temporal_indices[obj_key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (priority_scores[obj_key], temporal_indices[obj_key], obj_key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the priority scores of remaining entries to maintain consistent throughput, ensuring that frequently accessed entries are prioritized while adapting to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in priority_scores:
        del priority_scores[evicted_key]
        del temporal_indices[evicted_key]
    
    # Recalibrate priority scores
    for obj_key in cache_snapshot.cache:
        priority_scores[obj_key] *= RECALIBRATION_FACTOR
        heapq.heappush(priority_queue, (priority_scores[obj_key], temporal_indices[obj_key], obj_key))