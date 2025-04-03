# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
GQ_CAPACITY = 100  # Maximum number of items in the ghost queue

# Put the metadata specifically maintained by the policy below. The policy maintains access frequency, recency, predictive migration scores, contextual tags, and divides the cache into two FIFO queues (SQ and MQ) with a ghost queue (GQ) for evicted items. It tracks the frequency of each cached object and uses contextual insights from API orchestration.
access_frequency = defaultdict(int)
recency = defaultdict(int)
predictive_migration_scores = defaultdict(float)
contextual_tags = defaultdict(set)
SQ = deque()
MQ = deque()
GQ = deque()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy evaluates a composite score combining low access frequency, low recency, and low predictive migration scores, while considering contextual tags. If SQ exceeds its capacity, objects are moved to MQ until an eviction condition is met. GQ is used to track recently evicted items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Calculate composite score for each object in SQ and MQ
    def composite_score(key):
        return (access_frequency[key], recency[key], predictive_migration_scores[key])

    # Check if SQ exceeds its capacity
    if len(SQ) > 0:
        # Move objects from SQ to MQ until an eviction condition is met
        while len(SQ) > 0:
            key = SQ.popleft()
            MQ.append(key)
            if cache_snapshot.size + obj.size <= cache_snapshot.capacity:
                return key

    # Evaluate composite scores in MQ
    if len(MQ) > 0:
        candid_obj_key = min(MQ, key=composite_score)
        MQ.remove(candid_obj_key)

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency and recency of the object, updates its predictive migration score, and refines contextual tags. If the frequency is less than 3, it is incremented by 1.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    if access_frequency[obj.key] < 3:
        access_frequency[obj.key] += 1
    recency[obj.key] = cache_snapshot.access_count
    predictive_migration_scores[obj.key] += 0.1  # Example update
    contextual_tags[obj.key].add("hit")  # Example tag update

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy sets its access frequency to 1, initializes recency and predictive migration scores, and assigns contextual tags. If the object was in GQ, it is placed in MQ; otherwise, it goes to SQ.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] = 1
    recency[obj.key] = cache_snapshot.access_count
    predictive_migration_scores[obj.key] = 0.0
    contextual_tags[obj.key] = set()

    if obj.key in GQ:
        MQ.append(obj.key)
        GQ.remove(obj.key)
    else:
        SQ.append(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates predictive migration scores and updates contextual bindings. The evicted object is placed in GQ, and its frequency is no longer tracked. GQ is managed to maintain its capacity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    predictive_migration_scores[evicted_obj.key] *= 0.9  # Example recalibration
    contextual_tags[evicted_obj.key].add("evicted")  # Example tag update

    GQ.append(evicted_obj.key)
    if len(GQ) > GQ_CAPACITY:
        GQ.popleft()

    # Remove tracking of evicted object
    del access_frequency[evicted_obj.key]
    del recency[evicted_obj.key]
    del predictive_migration_scores[evicted_obj.key]
    del contextual_tags[evicted_obj.key]