from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from uuid import uuid4

@dataclass
class InterleavedItem:
    item_id: str
    source: str
    original_rank: int
    interleaved_rank: int

@dataclass
class Snapshot:
    snapshot_id: str
    items: list[InterleavedItem]
    created_at: datetime

@dataclass
class FeedSession:
    session_id: str
    snapshot: Snapshot
    created_at: datetime
    expires_at: datetime

class FeedSessionStore:
    """
    今回は検証のためメモリ上に保存する。
    実システムの場合はRedisやDBに保存する。
    """

    def __init__(self):
        self.sessions = {}

    def save(self, session):
        self.sessions[session.session_id] = session
    
    def get(self, session_id):
        return self.sessions.get(session_id)
    

def balanced_interleaving(ranking_a, ranking_b, start_with="A"):
    if start_with not in ("A", "B"):
        raise ValueError("start_with must be 'A' or 'B'")
    result = []
    seen = set()
    i = 0
    j = 0
    turn = start_with

    while i < len(ranking_a) or j < len(ranking_b):
        if turn == "A":
            while i < len(ranking_a) and ranking_a[i] in seen:
                i += 1
            if i < len(ranking_a):
                item_id = ranking_a[i]

                result.append(
                    InterleavedItem(
                        item_id=item_id,
                        source="A",
                        original_rank=i + 1,
                        interleaved_rank=len(result) + 1,
                    )
                )
                seen.add(item_id)
                i += 1
            turn = "B"
        else:
            while j < len(ranking_b) and ranking_b[j] in seen:
                j += 1
            if j < len(ranking_b):
                item_id = ranking_b[j]

                result.append(
                    InterleavedItem(
                        item_id=item_id,
                        source="B",
                        original_rank=j + 1,
                        interleaved_rank=len(result) + 1,
                    )
                )
                seen.add(item_id)
                j += 1
            turn = "A"

    return result

def create_snapshot(ranking_a, ranking_b, start_with="A"):
    items = balanced_interleaving(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with=start_with,
    )

    snapshot = Snapshot(
        snapshot_id="snap_shot_001",
        items=items,
        created_at=datetime.now(timezone.utc)
    )

    return snapshot

def create_feed_session(ranking_a, ranking_b, store, ttl_seconds=60):
    now = datetime.now(timezone.utc)

    snapshot = create_snapshot(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="A",
    )

    session = FeedSession(
        session_id=str(uuid4()),
        snapshot=snapshot,
        created_at=now,
        expires_at=now + timedelta(seconds=ttl_seconds),
    )

    store.save(session)

    return session

def is_expired(session, now=None):
    now = now or datetime.now(timezone.utc)
    return now >= session.expires_at

def get_page_by_cursor(session, cursor, limit):
    if limit <= 0:
        raise ValueError("limit must be greater than 0")
    
    start = cursor if cursor is not None else 0
    end = start + limit

    page_items = session.snapshot.items[start:end]

    if end >= len(session.snapshot.items):
        next_cursor = None
    else:
        next_cursor = end
    
    return page_items, next_cursor

if __name__ == "__main__":
    ranking_a = ["A1", "B2", "A2", "A3", "B3"]
    ranking_b = ["B1", "A2", "B2", "B4", "A3"]

    store = FeedSessionStore()

    session = create_feed_session(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        store=store,
        ttl_seconds=10,
    )

    print("session_id:", session.session_id)
    print("snapshot_id:", session.created_at)
    print("expired_at:", session.expires_at)
    print("is_expired:", is_expired(session))

    cursor = None
    limit = 3

    page1, cursor = get_page_by_cursor(session, cursor, limit)
    print("\npage1:", [item.item_id for item in page1])
    print("next_cursor:", cursor)

    # 本来のAPIでは、次回リクエストで session_id と cursor が渡ってくる想定
    loaded_session = store.get(session.session_id)

    page2, cursor = get_page_by_cursor(loaded_session, cursor, limit)
    print("\npage2:", [item.item_id for item in page2])
    print("next_cursor:", cursor)

    # 期限切れを擬似的に確認する
    future_time = session.expires_at + timedelta(seconds=1)

    print("\nfuture_time:", future_time)
    print("is_expired after future_time:", is_expired(session, now=future_time))
    