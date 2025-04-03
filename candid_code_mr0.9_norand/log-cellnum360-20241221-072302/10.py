# Import anything you need below
import heapq
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_FREQUENCY = 1
RETENTION_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a priority queue where each cache entry is associated with a priority score. The score is calculated based on a combination of the entry's age, frequency of access, and a retention factor that increases the priority of entries that have been in the cache longer. Additionally, a timestamp is maintained for each entry to track its age.
priority_queue = []
frequency_count = defaultdict(lambda: DEFAULT_FREQUENCY)
timestamps = {}

def calculate_priority_score(obj_key, cache_snapshot):
    age = cache_snapshot.access_count - timestamps[obj_key]
    frequency = frequency_count[obj_key]
    retention = RETENTION_FACTOR * age
    return age + frequency + retention

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score from the priority queue. This approach ensures that entries with low access frequency and short retention are pruned first, while older and frequently accessed entries are retained longer.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        score, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the priority score of the accessed entry by increasing its frequency count and recalculating its score based on the updated frequency and age. The entry is then repositioned in the priority queue to reflect its new priority.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    frequency_count[obj.key] += 1
    new_score = calculate_priority_score(obj.key, cache_snapshot)
    heapq.heappush(priority_queue, (new_score, obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on its age and a default frequency count. The new entry is added to the priority queue, and the queue is adjusted to maintain the correct order based on priority scores.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    timestamps[obj.key] = cache_snapshot.access_count
    initial_score = calculate_priority_score(obj.key, cache_snapshot)
    heapq.heappush(priority_queue, (initial_score, obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted entry from the priority queue and recalculates the retention factor for remaining entries to ensure that the cache adapts to changing access patterns and optimizes retention of valuable entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in frequency_count:
        del frequency_count[evicted_obj.key]
    if evicted_obj.key in timestamps:
        del timestamps[evicted_obj.key]
    # Recalculate retention factor for remaining entries
    for key in cache_snapshot.cache:
        new_score = calculate_priority_score(key, cache_snapshot)
        heapq.heappush(priority_queue, (new_score, key))