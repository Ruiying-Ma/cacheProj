# Import anything you need below
from collections import defaultdict
import heapq

# Put tunable constant parameters below
LATENCY_FACTOR = 1.0
FREQUENCY_FACTOR = 1.0
RECENCY_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue where each cache entry is associated with a priority score. This score is calculated based on access frequency, recency, and a latency factor that estimates the cost of fetching the data from the main memory. Additionally, a state synchronization flag is maintained to ensure consistency across distributed cache nodes.
priority_queue = []
priority_scores = {}
access_frequency = defaultdict(int)
access_recency = {}
latency_costs = {}
state_sync_flag = False

def calculate_priority_score(obj_key, cache_snapshot):
    frequency = access_frequency[obj_key]
    recency = cache_snapshot.access_count - access_recency[obj_key]
    latency = latency_costs.get(obj_key, 0)
    return (FREQUENCY_FACTOR * frequency) + (RECENCY_FACTOR / (recency + 1)) + (LATENCY_FACTOR * latency)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by choosing the entry with the lowest priority score from the priority queue. If multiple entries have the same score, the one with the highest latency cost is evicted first to minimize future latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        score, latency, obj_key = heapq.heappop(priority_queue)
        if obj_key in cache_snapshot.cache:
            candid_obj_key = obj_key
            break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased based on its current frequency and recency of access. The state synchronization flag is checked and updated if necessary to ensure consistency across nodes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    access_frequency[obj_key] += 1
    access_recency[obj_key] = cache_snapshot.access_count
    priority_scores[obj_key] = calculate_priority_score(obj_key, cache_snapshot)
    heapq.heappush(priority_queue, (priority_scores[obj_key], latency_costs.get(obj_key, 0), obj_key))
    global state_sync_flag
    state_sync_flag = True

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its priority score is initialized based on an estimated access pattern and latency cost. The state synchronization flag is set to indicate a change in the cache state, prompting updates across distributed nodes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    access_frequency[obj_key] = 1
    access_recency[obj_key] = cache_snapshot.access_count
    latency_costs[obj_key] = obj.size  # Assuming size as a proxy for latency cost
    priority_scores[obj_key] = calculate_priority_score(obj_key, cache_snapshot)
    heapq.heappush(priority_queue, (priority_scores[obj_key], latency_costs[obj_key], obj_key))
    global state_sync_flag
    state_sync_flag = True

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the priority queue is rebalanced to reflect the removal of the entry. The state synchronization flag is updated to ensure that all nodes are aware of the change, maintaining consistency across the system.
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
        del access_frequency[evicted_key]
        del access_recency[evicted_key]
        del latency_costs[evicted_key]
    global state_sync_flag
    state_sync_flag = True