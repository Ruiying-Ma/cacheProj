# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SQ_CAPACITY = 10
MQ_CAPACITY = 20
GQ_CAPACITY = 30

# Put the metadata specifically maintained by the policy below. The policy maintains two FIFO queues (SQ and MQ) with predetermined capacities, a ghost FIFO queue (GQ) with a predetermined capacity, access frequency for each cached object, a Q-table for action-value pairs, a policy network for selecting actions, and a temporal difference error tracker for learning updates.
SQ = deque()
MQ = deque()
GQ = deque()
frequency = defaultdict(int)
Q_table = defaultdict(lambda: defaultdict(float))
policy_network = defaultdict(float)
temporal_difference_error = defaultdict(float)

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
    if len(SQ) > SQ_CAPACITY:
        while len(SQ) > SQ_CAPACITY:
            moved_obj = SQ.popleft()
            if frequency[moved_obj.key] < 2 or len(MQ) >= MQ_CAPACITY:
                candid_obj_key = moved_obj.key
                break
            MQ.append(moved_obj)
    if len(MQ) >= MQ_CAPACITY:
        while len(MQ) >= MQ_CAPACITY:
            reduced_obj = MQ.popleft()
            frequency[reduced_obj.key] -= 1
            if frequency[reduced_obj.key] == 0:
                candid_obj_key = reduced_obj.key
                break
            MQ.append(reduced_obj)
    if candid_obj_key is None:
        # Fallback to evict the least recently used in SQ if no candidate found
        candid_obj_key = SQ.popleft().key
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
    if frequency[obj.key] < 3:
        frequency[obj.key] += 1
    # Update Q-value using temporal difference learning
    reward = 1  # Reward for a cache hit
    current_state = tuple(cache_snapshot.cache.keys())
    next_state = current_state  # Assuming state doesn't change for simplicity
    alpha = 0.1  # Learning rate
    gamma = 0.9  # Discount factor
    Q_table[current_state][obj.key] += alpha * (reward + gamma * max(Q_table[next_state].values()) - Q_table[current_state][obj.key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The policy sets the inserted object's frequency to 1. If the object was in GQ, it is placed at the rear of MQ and removed from GQ; otherwise, it is placed at the rear of SQ. The Q-table is updated to reflect the new state of the cache, and the policy network is adjusted to improve future action selections.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    frequency[obj.key] = 1
    if obj.key in GQ:
        GQ.remove(obj.key)
        MQ.append(obj)
    else:
        SQ.append(obj)
    # Update Q-table to reflect new state
    current_state = tuple(cache_snapshot.cache.keys())
    Q_table[current_state][obj.key] = 0  # Initialize Q-value for new state-action pair

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
    if len(GQ) >= GQ_CAPACITY:
        GQ.popleft()
    GQ.append(evicted_obj.key)
    # Update Q-value for evicted object
    current_state = tuple(cache_snapshot.cache.keys())
    reward = -1  # Penalty for eviction
    alpha = 0.1  # Learning rate
    gamma = 0.9  # Discount factor
    Q_table[current_state][evicted_obj.key] += alpha * (reward + gamma * max(Q_table[current_state].values()) - Q_table[current_state][evicted_obj.key])