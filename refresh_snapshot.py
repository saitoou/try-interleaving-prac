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

def refresh_session(session, ranking_a, ranking_b, store, ttl_seconds=60):
    """
    TTL切れ時にsnapshotを作り直す。
    今回はまだ表示済みitemの除外はしない。
    """
    now = datetime.now(timezone.utc)
    new_snapshot = create_snapshot(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="A",
    )
    session.snapshot = new_snapshot
    session.expires_at = now + timedelta(seconds=ttl_seconds)

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

def get_page(store, session_id, cursor, ranking_a, ranking_b, limit, ttl_seconds=60, now=None):
    """
    session_idとcursorを使ってページを取得する。
    sessionが期限切れならsnapshotをrefreshする。
    """
    now = now or datetime.now(timezone.utc)
    session = store.get(session_id)

    if session is None:
        session = create_feed_session(
            ranking_a=ranking_a,
            ranking_b=ranking_b,
            store=store,
            ttl_seconds=ttl_seconds,
        )
        cursor = None
    elif is_expired(session, now=now):
        session = refresh_session(
            session=session,
            ranking_a=ranking_a,
            ranking_b=ranking_b,
            store=store,
            ttl_seconds=ttl_seconds,
        )
        # 古いsnapshotのcursor位置は、新しいsnapshotでは意味が変わる。
        # そのためrefresh後は0から読み直す。
        cursor = None
    
    page_items, next_cursor = get_page_by_cursor(
        session=session,
        cursor=cursor,
        limit=limit,
    )

    return session, page_items, next_cursor


if __name__ == "__main__":
    store = FeedSessionStore()

    ranking_a_v1 = ["A1", "B2", "A2", "A3", "B3"]
    ranking_b_v1 = ["B1", "A2", "B2", "B4", "A3"]

    session = create_feed_session(
        ranking_a=ranking_a_v1,
        ranking_b=ranking_b_v1,
        store=store,
        ttl_seconds=10,
    )

    print("initial session_id:", session.session_id)
    print("initial snapshot_id:", session.snapshot.snapshot_id)
    print("initial snapshot:", [item.item_id for item in session.snapshot.items])

    cursor = None
    limit = 3

    page1, cursor = get_page_by_cursor(session, cursor, limit)
    print("\npage1:", [item.item_id for item in page1])
    print("next_cursor:", cursor)

    page2, cursor = get_page_by_cursor(session, cursor, limit)
    print("\npage2:", [item.item_id for item in page2])
    print("next_cursor:", cursor)

    # ここでランキングが変わった想定
    ranking_a_v2 = ["A3", "A1", "A4", "B5", "A5"]
    ranking_b_v2 = ["B4", "B1", "B6", "A2", "B7"]

    # 期限切れ後の時刻を作る
    expired_time = session.expires_at + timedelta(seconds=1)

    session, page_after_refresh, cursor = get_page(
        store=store,
        session_id=session.session_id,
        cursor=cursor,
        ranking_a=ranking_a_v2,
        ranking_b=ranking_b_v2,
        limit=3,
        ttl_seconds=10,
        now=expired_time,
    )

    print("\nafter refresh snapshot_id:", session.snapshot.snapshot_id)
    print("after refresh snapshot:", [item.item_id for item in session.snapshot.items])
    print("page after refresh:", [item.item_id for item in page_after_refresh])
    print("next_cursor:", cursor)
    