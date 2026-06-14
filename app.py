
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
                item = ranking_a[i]
                result.append(item)
                seen.add(item)
                i += 1

            turn = "B"

        else:
            while j < len(ranking_b) and ranking_b[j] in seen:
                j += 1
            
            if j < len(ranking_b):
                item = ranking_b[j]
                result.append(item)
                seen.add(item)
                j += 1

            turn = "A"

    
    return result

if __name__ == "__main__":
    ranking_a = ["A1", "B2", "A2", "A3", "B3"]
    ranking_b = ["B1", "A2", "B2", "B4", "A3"]

    result = balanced_interleaving(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="A",
    )

    print(result)