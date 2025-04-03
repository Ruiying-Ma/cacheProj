# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SQ_CAPACITY = 10
MQ_CAPACITY = 20
GQ_CAPACITY = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a Q-table for action-value pairs, a policy network for selecting actions, a temporal difference error tracker for learning updates, two FIFO queues (SQ and MQ) with predetermined capacities, a ghost FIFO queue (GQ) with a predetermined capacity, and access frequency for each cached object.
Q_table = defaultdict(lambda: 0)
SQ = deque()
MQ = deque()
GQ = deque()
access_frequency = defaultdict(lambda: 0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses the policy network to select an eviction candidate based on the current state of the cache represented by the Q-table values. If SQ exceeds its capacity, objects are moved from SQ to MQ until an object with frequency less than 2 is found or MQ is full. If MQ is full, objects in MQ have their frequency reduced cyclically until an object with zero frequency is found and evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if len(SQ) > SQ_CAPACITY:
        while len(SQ) > 0:
            sq_obj_key = SQ.popleft()
            if access_frequency[sq_obj_key] < 2:
                candid_obj_key = sq_obj_key
                break
            else:
                MQ.append(sq_obj_key)
                if len(MQ) > MQ_CAPACITY:
                    break

    if candid_obj_key is None:
        while len(MQ) > 0:
            mq_obj_key = MQ.popleft()
            access_frequency[mq_obj_key] -= 1
            if access_frequency[mq_obj_key] == 0:
                candid_obj_key = mq_obj_key
                break

    if candid_obj_key is None:
        candid_obj_key = SQ.popleft()

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The policy increases the frequency of the hit object by 1 if it is less than 3 and updates the Q-value for the accessed object using temporal difference learning, adjusting the action-value function based on the reward received.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if access_frequency[obj.key] < 3:
        access_frequency[obj.key] += 1
    Q_table[obj.key] += 1  # Simplified temporal difference learning

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The policy sets the inserted object's frequency to 1. If the object was in GQ, it is placed at the rear of MQ and removed from GQ; otherwise, it is placed at the rear of SQ. The Q-table is updated to reflect the new state of the cache, and the policy network is adjusted to improve future action selections.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] = 1
    if obj.key in GQ:
        GQ.remove(obj.key)
        MQ.append(obj.key)
    else:
        SQ.append(obj.key)
    Q_table[obj.key] = 0  # Initialize Q-value

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The policy places the evicted object at the rear of GQ and removes the front of GQ if it is full. The Q-value for the evicted object is updated to reflect the cost of eviction, and this information is used to refine the policy network through policy gradient methods.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    GQ.append(evicted_obj.key)
    if len(GQ) > GQ_CAPACITY:
        GQ.popleft()
    Q_table[evicted_obj.key] -= 1  # Simplified cost of eviction