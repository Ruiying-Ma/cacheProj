# Import anything you need below
import heapq
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY = 1
ANOMALY_DETECTION_THRESHOLD = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a priority queue for cache objects based on access frequency and recency, a data threshold for each object to determine its importance, and an anomaly detection score to identify unusual access patterns.
priority_queue = []  # Min-heap based on priority
object_metadata = defaultdict(lambda: {'priority': INITIAL_PRIORITY, 'access_count': 0, 'anomaly_score': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest priority in the queue, considering both its data threshold and anomaly detection score. Objects with low importance and normal access patterns are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while priority_queue:
        priority, key = heapq.heappop(priority_queue)
        if key in cache_snapshot.cache:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's priority is increased in the queue, its data threshold is re-evaluated, and its anomaly detection score is updated to reflect the recent access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    metadata = object_metadata[obj.key]
    metadata['access_count'] += 1
    metadata['priority'] += 1
    metadata['anomaly_score'] = metadata['access_count'] / cache_snapshot.access_count
    
    heapq.heappush(priority_queue, (metadata['priority'], obj.key))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority based on its data threshold and sets an initial anomaly detection score. The object is then placed in the priority queue accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    metadata = object_metadata[obj.key]
    metadata['priority'] = INITIAL_PRIORITY
    metadata['access_count'] = 1
    metadata['anomaly_score'] = 0
    
    heapq.heappush(priority_queue, (metadata['priority'], obj.key))

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy adjusts the priority queue to reflect the removal, recalibrates the data thresholds of remaining objects if necessary, and updates the anomaly detection model to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in object_metadata:
        del object_metadata[evicted_obj.key]
    
    # Rebuild the priority queue to remove stale entries
    global priority_queue
    priority_queue = [(metadata['priority'], key) for key, metadata in object_metadata.items() if key in cache_snapshot.cache]
    heapq.heapify(priority_queue)