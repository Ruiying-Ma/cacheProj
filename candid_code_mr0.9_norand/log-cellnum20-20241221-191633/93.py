# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
ANOMALY_THRESHOLD = 0.1
PRIORITY_ADJUSTMENT_FACTOR = 1.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a dynamic priority score for each cache entry. It also tracks global cache performance metrics such as hit rate and anomaly detection indicators.
access_frequency = defaultdict(int)
recency_of_access = {}
dynamic_priority_score = {}
anomaly_detected = False

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on the lowest dynamic priority score, which is continuously adjusted based on access patterns and real-time feedback. Anomalies in access patterns trigger a temporary increase in the priority score to prevent premature eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        priority = dynamic_priority_score[key]
        if priority < min_priority:
            min_priority = priority
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are updated. The dynamic priority score is recalculated using a feedback loop that considers the current hit rate and any detected anomalies.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] += 1
    recency_of_access[obj.key] = cache_snapshot.access_count
    hit_rate = cache_snapshot.hit_count / cache_snapshot.access_count
    anomaly_factor = PRIORITY_ADJUSTMENT_FACTOR if anomaly_detected else 1
    dynamic_priority_score[obj.key] = (access_frequency[obj.key] / (cache_snapshot.access_count - recency_of_access[obj.key] + 1)) * anomaly_factor

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency metadata. The dynamic priority score is set based on initial access predictions and adjusted using real-time monitoring data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    access_frequency[obj.key] = 1
    recency_of_access[obj.key] = cache_snapshot.access_count
    dynamic_priority_score[obj.key] = 1 / obj.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates global performance metrics and checks for anomalies. If an anomaly is detected, it adjusts the priority scoring mechanism to correct potential biases in future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    global anomaly_detected
    hit_rate = cache_snapshot.hit_count / cache_snapshot.access_count
    if abs(hit_rate - (cache_snapshot.hit_count - 1) / (cache_snapshot.access_count - 1)) > ANOMALY_THRESHOLD:
        anomaly_detected = True
    else:
        anomaly_detected = False
    # Clean up metadata for evicted object
    if evicted_obj.key in access_frequency:
        del access_frequency[evicted_obj.key]
    if evicted_obj.key in recency_of_access:
        del recency_of_access[evicted_obj.key]
    if evicted_obj.key in dynamic_priority_score:
        del dynamic_priority_score[evicted_obj.key]