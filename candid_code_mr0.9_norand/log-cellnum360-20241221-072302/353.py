# Import anything you need below
import hashlib
from collections import defaultdict

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a distributed ledger that records access frequency, recency, and a cryptographic hash of each cache entry. Each entry is validated through a consensus mechanism involving decentralized nodes that vote on the legitimacy of the metadata updates.
ledger = {
    'access_frequency': defaultdict(int),
    'recency': {},
    'hash': {}
}

def generate_hash(obj):
    # Generate a cryptographic hash for the object
    return hashlib.sha256(obj.key.encode()).hexdigest()

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by reaching a consensus among decentralized nodes, prioritizing entries with the lowest access frequency and recency scores. If a tie occurs, the entry with the oldest cryptographic hash is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_frequency = float('inf')
    min_recency = float('inf')
    oldest_hash = None

    for key, cached_obj in cache_snapshot.cache.items():
        frequency = ledger['access_frequency'][key]
        recency = ledger['recency'][key]
        obj_hash = ledger['hash'][key]

        if (frequency < min_frequency or
            (frequency == min_frequency and recency < min_recency) or
            (frequency == min_frequency and recency == min_recency and (oldest_hash is None or obj_hash < oldest_hash))):
            min_frequency = frequency
            min_recency = recency
            oldest_hash = obj_hash
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and recency scores in the distributed ledger are updated, and a new cryptographic hash is generated for the entry. The update is validated through a consensus mechanism among the nodes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    ledger['access_frequency'][obj.key] += 1
    ledger['recency'][obj.key] = cache_snapshot.access_count
    ledger['hash'][obj.key] = generate_hash(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the distributed ledger is updated with initial access frequency and recency scores, and a cryptographic hash is generated. The insertion is validated by the consensus mechanism to ensure decentralized governance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    ledger['access_frequency'][obj.key] = 1
    ledger['recency'][obj.key] = cache_snapshot.access_count
    ledger['hash'][obj.key] = generate_hash(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the distributed ledger is updated to remove the entry, and the change is validated through the consensus mechanism. The nodes adjust their governance parameters to reflect the eviction decision.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in ledger['access_frequency']:
        del ledger['access_frequency'][evicted_obj.key]
    if evicted_obj.key in ledger['recency']:
        del ledger['recency'][evicted_obj.key]
    if evicted_obj.key in ledger['hash']:
        del ledger['hash'][evicted_obj.key]