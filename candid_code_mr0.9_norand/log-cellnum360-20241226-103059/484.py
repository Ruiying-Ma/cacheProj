# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
EEM_INITIAL_SCORE = 1
EEM_HIT_INCREMENT = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a lightweight FIFO queue and a simplified Entropic Entanglement Matrix (EEM). The FIFO queue tracks insertion order, while the EEM measures basic relevance and interdependencies between cached objects.
fifo_queue = deque()
eem = defaultdict(lambda: defaultdict(int))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    During eviction, a subset of entries from the front of the FIFO queue is selected. The entry with the lowest relevance score in the EEM is evicted, balancing temporal order and basic relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_relevance_score = float('inf')
    
    # Check a subset of entries from the front of the FIFO queue
    for key in list(fifo_queue)[:min(len(fifo_queue), 5)]:  # Check first 5 or less
        relevance_score = sum(eem[key].values())
        if relevance_score < min_relevance_score:
            min_relevance_score = relevance_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the EEM is updated to strengthen entanglements with recently accessed entries, reinforcing their relevance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    for key in fifo_queue:
        if key != obj.key:
            eem[obj.key][key] += EEM_HIT_INCREMENT
            eem[key][obj.key] += EEM_HIT_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed at the rear of the FIFO queue, and the EEM is updated to establish initial entanglements with existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj.key)
    for key in fifo_queue:
        if key != obj.key:
            eem[obj.key][key] = EEM_INITIAL_SCORE
            eem[key][obj.key] = EEM_INITIAL_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the FIFO queue is updated by removing the evicted entry, and the EEM is adjusted to dissolve entanglements related to the evicted object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.remove(evicted_obj.key)
    del eem[evicted_obj.key]
    for key in eem:
        if evicted_obj.key in eem[key]:
            del eem[key][evicted_obj.key]