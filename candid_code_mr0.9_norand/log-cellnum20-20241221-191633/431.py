# Import anything you need below
import heapq
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_FREQUENCY = 1
BASE_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a synchronized cache with metadata including a priority queue for event-driven access patterns, a thread coordination map to track thread-specific access frequencies, and a timestamp for each cache entry to manage recency.
priority_queue = []  # Min-heap for priority queue
thread_coordination_map = defaultdict(lambda: DEFAULT_FREQUENCY)
timestamps = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of the lowest priority in the event-driven queue and the least recently used timestamp, ensuring that less frequently accessed and older entries are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        priority, timestamp, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the thread coordination map to increase the access frequency for the corresponding thread, adjusts the priority in the event-driven queue to reflect increased importance, and refreshes the timestamp to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    thread_coordination_map[obj.key] += 1
    new_priority = -thread_coordination_map[obj.key]
    timestamps[obj.key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (new_priority, timestamps[obj.key], obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the thread coordination map entry for the object with a default frequency, assigns a base priority in the event-driven queue, and sets the current timestamp for recency tracking.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    thread_coordination_map[obj.key] = DEFAULT_FREQUENCY
    timestamps[obj.key] = cache_snapshot.access_count
    heapq.heappush(priority_queue, (-BASE_PRIORITY, timestamps[obj.key], obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the entry from the thread coordination map, deletes its priority from the event-driven queue, and clears the timestamp, ensuring all metadata is consistent and up-to-date.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in thread_coordination_map:
        del thread_coordination_map[evicted_obj.key]
    if evicted_obj.key in timestamps:
        del timestamps[evicted_obj.key]
    # No need to remove from priority_queue explicitly as it will be ignored in future evictions