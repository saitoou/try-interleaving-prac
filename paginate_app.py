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

def paginate(items, page, page_size):
    if page < 1:
        raise ValueError("page must be greater than or equal to 1")
    
    if page_size <= 0:
        raise ValueError("page_size must be greater than 0")
    
    start = (page - 1) * page_size
    end = start + page_size

    return items[start:end]

if __name__ == "__main__":
    ranking_a = ["A1", "B2", "A2", "A3", "B3"]
    ranking_b = ["B1", "A2", "B2", "B4", "A3"]

    interlaved = balanced_interleaving(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="A",
    )

    page_size = 3

    page1 = paginate(interlaved, page=1, page_size=page_size)
    page2 = paginate(interlaved, page=2, page_size=page_size)
    page3 = paginate(interlaved, page=3, page_size=page_size)

    print("page1")
    for item in page1:
        print(item)
    print("\npage2")
    for item in page2:
        print(item)
    print("\npage3")
    for item in page3:
        print(item)

