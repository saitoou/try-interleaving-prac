from dataclasses import dataclass
from datetime import datetime, timezone

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

def get_page_by_cursor(snapshot, cursor, limit):
    if limit <= 0:
        raise ValueError("limit must be greater than 0")
    
    start = cursor if cursor is not None else 0
    end = start + limit

    page_items = snapshot.items[start:end]

    if end >= len(snapshot.items):
        next_cursor = None
    else:
        next_cursor = end
    
    return page_items, next_cursor

if __name__ == "__main__":
    ranking_a = ["A1", "B2", "A2", "A3", "B3"]
    ranking_b = ["B1", "A2", "B2", "B4", "A3"]

    snapshot = create_snapshot(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="A",
    )

    print("snapshot_id:", snapshot.snapshot_id)
    print("created_at:", snapshot.created_at)
    print("snapshot items:", [item.item_id for item in snapshot.items])

    cursor = None
    limit = 3

    page1, cursor = get_page_by_cursor(snapshot, cursor, limit)
    print("\npage1:", [item.item_id for item in page1])
    print("next_cursor:", cursor)

    page2, cursor = get_page_by_cursor(snapshot, cursor, limit)
    print("\npage2:", [item.item_id for item in page2])
    print("next_cursor:", cursor)

    page3, cursor = get_page_by_cursor(snapshot, cursor, limit)
    print("\npage3:", [item.item_id for item in page3])
    print("next_cursor:", cursor)