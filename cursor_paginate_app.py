from dataclasses import dataclass

@dataclass
class InterleavedItem:
    item_id: str
    source: str
    original_rank: int
    interleaved_rank: int

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

def get_page_by_cursor(items, cursor, limit):
    if limit <= 0:
        raise ValueError("limit must be greater than 0")
    
    start = cursor if cursor is not None else 0
    end = start + limit

    page_item = items[start:end]

    if end >= len(items):
        next_cursor = None
    else:
        next_cursor = end
    
    return page_item, next_cursor


if __name__ == "__main__":
    ranking_a = ["A1", "B2", "A2", "A3", "B3"]
    ranking_b = ["B1", "A2", "B2", "B4", "A3"]

    interleaved = balanced_interleaving(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="A",
    )

    cursor = None
    limit = 3

    page1, cursor = get_page_by_cursor(interleaved, cursor, limit)
    print("page1")
    for item in page1:
        print(item)
    print("next_cursor:", cursor)

    page2, cursor = get_page_by_cursor(interleaved, cursor, limit)
    print("\npage2")
    for item in page2:
        print(item)
    print("next_cursor:", cursor)

    page3, cursor = get_page_by_cursor(interleaved, cursor, limit)
    print("\npage3")
    for item in page3:
        print(item)
    print("next_cursor:", cursor)