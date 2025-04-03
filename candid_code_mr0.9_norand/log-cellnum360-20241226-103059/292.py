# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
NEUTRAL_ENTROPY = 1.0
BASELINE_PSS = 1.0
ENTROPY_DECREASE_ON_HIT = 0.1
PSS_INCREASE_ON_HIT = 0.1
ENTROPY_RECALIBRATION_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue for order tracking, a simplified Quantum Entropic Map (QEM) for entropy states, and a Predictive Signal Score (PSS) for access trends.
fifo_queue = deque()
qem = defaultdict(lambda: NEUTRAL_ENTROPY)
pss = defaultdict(lambda: BASELINE_PSS)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a subset of entries from the front of the FIFO queue and evicts the one with the highest entropy in the QEM, balancing FIFO order with entropy-informed decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    subset_size = min(len(fifo_queue), 5)  # Arbitrary subset size for eviction consideration
    max_entropy = -1

    for _ in range(subset_size):
        key = fifo_queue.popleft()
        entropy = qem[key]
        if entropy > max_entropy:
            max_entropy = entropy
            candid_obj_key = key
        fifo_queue.append(key)  # Re-add to maintain order

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QEM reduces the entropy of the accessed entry, the PSS is incrementally adjusted to reflect increased access likelihood, and the FIFO queue remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    qem[key] = max(0, qem[key] - ENTROPY_DECREASE_ON_HIT)
    pss[key] += PSS_INCREASE_ON_HIT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed at the rear of the FIFO queue, the QEM assigns a neutral entropy value, and the PSS is initialized with a baseline score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    fifo_queue.append(key)
    qem[key] = NEUTRAL_ENTROPY
    pss[key] = BASELINE_PSS

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the evicted object is removed from the front of the FIFO queue, the QEM redistributes entropy among remaining entries, and the PSS is recalibrated to maintain access predictability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    fifo_queue.remove(evicted_key)
    del qem[evicted_key]
    del pss[evicted_key]

    # Recalibrate entropy and PSS for remaining entries
    for key in fifo_queue:
        qem[key] *= ENTROPY_RECALIBRATION_FACTOR
        pss[key] *= ENTROPY_RECALIBRATION_FACTOR