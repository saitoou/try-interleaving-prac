# Balanced Interleavingについて考える（他のInterleavingもあり）

## Interleavingとは
- インターリービングは二つのシステムのデザインや動きなどを検証する際にA/Bテストを導入することがあると思います。単純なサイトで比較対象システムが簡易であればA/Bテストだけを用いれば良いのですが、PV数の少ない場合やテスト対象とするシステムが複数ある場合は、インターリービングというアルゴリズムを使用して比較するのが近年？（だいぶまえ）の手法となっています。

インターリービングという単語の意味は複数のあるものを交互に混ぜるみたいな意味であり、その意味の通り特定のランキングAと特定のランキングBを交互に混ぜて出力させる仕組みです。
主に検索や推薦システムのランキングを出力するシステムに適用します。

## 様々な種類のInterleaving
- インターリービングの中でも比較の対象となるものが二つの場合と複数の場合とで様々なインターリービングがあります。今回は二つの比較について取り上げるため、複数は割愛します。
[このリンクで様々なinterleavingが試せます。](https://github.com/mpkato/interleaving)

以下のように特定のAとBのランキングがあった際に交互に混じったものを出力します。
A: [A1, A2, A3, A4, A5]
B: [B1, B2, B3, B4, B5]
Interleaving: [A1, B1, A2, B2, A3, B3]...

上記のようなイメージです。

## 二つのランキングのためのインターリービング
二つのランキングを比較していくインターリービングは以下の種類のものがあります。

1. Balanced Interleaving
2. Team draft Interleaving
3. Probabilistic Interleaving
4. Optimized Interleaving

### Balanced Interleaving
1の `Balanced Interleaving` は、以下のようなランキングがあったとします。
A: [A1, B2, A2, A3, B3]
B: [B1, A2, B2, B4, A3]

最初にA, Bどちらのランキングが先に来るかを決めます。そしてA, B, 上位のアイテムから順に交互に選択して混合のリストを作っていきます。同じアイテムが重複した場合はスキップされて新しいアイテムが追加されます。
A, Bを並び替えたものはAを最初の先頭とすると、
[A1, B1, B2, A2...]と順に並ぶが次はAのランキングはA2があるがすでにBのランキングでA2が上位にあり、すでに混合ランキングに入っているので飛ばされて、さらにB2もあるため飛ばされて、A3がくる。最終的に[A1, B1, B2, A2, A3, B4, B3, ...]となる。表示結果の混合ランキングとどのランキングが先頭に採用されたかをもっておき、評価する。

### Team draft Interleaving

2の `Team draft Interleaving` は、以下のようなランキングがあったとします。
A: [A1, B2, A3]
B: [B1, A2, B4]

A, Bのランキングがあり、名前の通りチームをドラフトします。A, Bのどちらのランキングを先に指名するかランダムに決めて、その後のランキングはA, Bのランキングからとった二つのデータ（ここでいうA1やB1、A2やB2などのこと）をランダムに決定して並べていきます。よりドラフト的にいうと、
`次のどちらのチーム、A/Bのランキングのどちらが指名するかを決める。選ばれたチームは自分のランキングの中でまだ出ていない最上位のアイテムを取る`
というイメージです。複数通りのランキングができます。
2-1. [A1, B1, B2...]
2-2. [A1, B1, A2...]
2-3. [B1, A1. B2...]
2-4. [B1, A1, A2...]


### Probabilistic Interleaving

1と2では混合ランキングを各ランキングから順位を保ちながら選択していました。
3の `Probabilistic Interleaving` は、A/Bのランキングを確率分布として扱い、上位ほど選ばれやすいようにランダムに混ぜてランキングを生成する方法です。
AのランキングとBのランキングを両方見て、各アイテムが選ばれる確率を作成し、その確率に従って、次に出すアイテムをランダムに選択します。
たとえば、以下のようなAとBのランキングがあります。
A: [A1, B2, A2]
B: [B1, A2, B2]
これらは重みづけすると、上位が強いためA1-> 3, B2-> 2, A2-> 1のようにして評価します。Bも同様にして。B1-> 3, A2-> 2, B2-> 1となり、
A1: 3, B1: 3, B2: 2(Aの重み) + 1(Bの重み), A2: 1 + 2となって、A1, B1, B2, A2は全て3となり、ほぼ同じ確率で選ばれます。もっと順位差出るように確率式を使います。`重み = 1 / rank ^ τ` のようにして重みを再計算します。
たとえばτが3の場合は、1位の場合は、1/ 1^3 = 1, 2位の場合は、1/ 2^3 = 0.125, 3位の場合は、1/ 3^3 = 0.037となり、１が選ばれやすくなります。これらを先ほどのランキングの要素に反映すると、以下のようになりA1とB1がかなり選ばれやすくなり、B2とA2が選ばれにくくなります。
```
A.
A1: 1.000
B2: 0.125
A2: 0.037
B.
B1: 1.000
A2: 0.125
B2: 0.037
合算.
A1: 1.000
B1: 1.000
B2: 0.125 + 0.037 = 0.162
A2: 0.037 + 0.125 = 0.162
```
全体の重みは、2.324なので確率としては以下のようになります。
```
A1: 43.0%
B1: 43.0%
B2: 7.0%
A2: 7.0%
```
これに従って1個目を選択します。1個目にA1が選ばれたとして、次を選ぶ場合A1は候補から外して残りはB1,B2, A2となります。
残りのランキングで確率を作り、合計はB1: 1.000, B2: 0.162, A2: 0.162で合計は1.324で確率は、B1: 75.5%, B2: 12.2%, A2: 12.2%となります。
ここでB1が選ばれて、次は、、、という感じで確率を出して選択していきます。確率が上位のものが選ばれやすいですが、上位順になるわけではないのがあります。
こちらも確率で選んでいるので混合ランキングは複数パターンあります。

### Optimized Interleaving

4の `Optimized Interleaving`は、公平に比較できるように、どの混合ランキングを出すかを最適化して選ぶの方法です。
これも解説したいですが、本記事は1のアルゴリズムを使って発展したので、割愛します。知りたい場合は`### 今回の記事の参照先`のリンクを参照してください。

## 本題
以下の要件があったとします。
- ランキングデータが800件以上ある
- 何ページにも分かれる
- ページをまたいでの重複表示は絶対に許されない
- A/Bのランキングを混ぜたい

これを考慮して最適な方法を選び、今回は`Balanced Interleaving`を選択して要件を設計、実装します。なおライブラリは使用しないでいきます。
ページネーションは、offset法やcursor法などがありますが、今回はデータ量がかなり多く`特に重複を許されない`のでcursor法を選択します。
また、ランキングはリアルタイムで変わると思いますし、ユーザーがページをめくった瞬間にも順位を並べて表示しなければなりません。これらのことを考慮すると全体的に最初に混合ランキングを生成し、整列させたランキングのスナップショットを持ち、それらを並べていこうと思いました。
単純にリアルタイムで並び替えは事故りやすいなと思ったのと、現実的ではないなと思いスナップショットを取ることを考えました。またこのスナップショットは一定時間で更新するようにすれば、最新ランキングを反映できます。
（同じ閲覧セッション中は同じスナップショットを使用し、新規アクセス時やリフレッシュ時、期限切れの際に新しいスナップショットを作る考えです。）

## 実装
- 上記の要件と、選択した設計を考慮して実装していきます。
```
Balanced Interleaving
+ snapshot
+ cursor pagination
+ session TTL
+ expired時はsnapshot再生成
+ ただし、すでに表示済みのitem_idは除外
```

まずは`Balanced Interleaving`のアルゴリズムを実装します。
以下のようにranking_aとranking_bを用意し、seenというset()とresultの空配列を用意します。pythonのset()は重複を許さないので、この性質をうまく活用し混合ランキングを作成する。
```python
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
```
実行すると以下のように、AとBのランキングを並び替えてくれます。
```bash
➜  interliaving-try python app.py   
['A1', 'B1', 'B2', 'A2', 'A3', 'B4', 'B3']
```

次はitemにメタ情報を持たせるようにします。どのランキングから来たか、A,Bのランキングの順位はどのくらいかを情報で入れます。

```python
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

if __name__ == "__main__":
    ranking_a = ["A1", "B2", "A2", "A3", "B3"]
    ranking_b = ["B1", "A2", "B2", "B4", "A3"]

    result = balanced_interleaving(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="B",
    )
    for item in result:
        print(item)
```

```bash
➜  interliaving-try python meta_app.py
InterleavedItem(item_id='A1', source='A', original_rank=1, interleaved_rank=1)
InterleavedItem(item_id='B1', source='B', original_rank=1, interleaved_rank=2)
InterleavedItem(item_id='B2', source='A', original_rank=2, interleaved_rank=3)
InterleavedItem(item_id='A2', source='B', original_rank=2, interleaved_rank=4)
InterleavedItem(item_id='A3', source='A', original_rank=4, interleaved_rank=5)
InterleavedItem(item_id='B4', source='B', original_rank=4, interleaved_rank=6)
InterleavedItem(item_id='B3', source='A', original_rank=5, interleaved_rank=7)
```

次にpaginationの要素を追加していきます。
関数やデータクラスは変わらずですが、新たにpaginate()を追加します。
start番目の要素からend番目の直前の要素を取得します。
1ページの場合は、start=0, end=3としてresult[0:3]で取得し、2ページの場合は、start=3, end=6としてresult[3:6]として要素を取得し、返します。

```python
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
```

以前はpage番号として取得していましたが、次はcursor方式に変更します。
差分だけコードを追加します。

```python
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
```

```bash
page1
InterleavedItem(item_id='A1', source='A', original_rank=1, interleaved_rank=1)
InterleavedItem(item_id='B1', source='B', original_rank=1, interleaved_rank=2)
InterleavedItem(item_id='B2', source='A', original_rank=2, interleaved_rank=3)
next_cursor: 3

page2
InterleavedItem(item_id='A2', source='B', original_rank=2, interleaved_rank=4)
InterleavedItem(item_id='A3', source='A', original_rank=4, interleaved_rank=5)
InterleavedItem(item_id='B4', source='B', original_rank=4, interleaved_rank=6)
next_cursor: 6

page3
InterleavedItem(item_id='B3', source='A', original_rank=5, interleaved_rank=7)
next_cursor: None
```

cursorとして次のページに表示する要素の位置を保持して、次がもうない場合はNoneが入っています。
snapshotを付け足していきます。

```python
@dataclass
class Snapshot:
    snapshot_id: str
    items: list[InterleavedItem]
    created_at: datetime

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
```
```bash
➜  interliaving-try python snapshot.py           
snapshot_id: snap_shot_001
created_at: 2026-06-14 14:33:52.795759+00:00
snapshot items: ['A1', 'B1', 'B2', 'A2', 'A3', 'B4', 'B3']

page1: ['A1', 'B1', 'B2']
next_cursor: 3

page2: ['A2', 'A3', 'B4']
next_cursor: 6

page3: ['B3']
next_cursor: None
```

snapshotを定義して、実行時に混合ランキングの配列を取得して保存するようにします。
次はsession_idを付け足して、今見ているユーザーのセッションではこのsnapshotを使用することを実装します。

```python
@dataclass
class FeedSession:
    session_id: str
    snapshot: Snapshot
    created_at: datetime

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
    
def create_feed_session(ranking_a, ranking_b, store):
    snapshot = create_snapshot(
        ranking_a=ranking_a,
        ranking_b=ranking_b,
        start_with="A",
    )

    session = FeedSession(
        session_id=str(uuid4()),
        snapshot=snapshot,
        created_at=datetime.now(timezone.utc)
    )

    store.save(session)

    return session

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
    )

    print("session_id:", session.session_id)
    print("snapshot_id:", session.snapshot.snapshot_id)
    print("snapshot items:", [item.item_id for item in session.snapshot.items])

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

    loaded_session = store.get(session.session_id)

    page3, cursor = get_page_by_cursor(loaded_session, cursor, limit)
    print("\npage3:", [item.item_id for item in page3])
    print("next_cursor:", cursor)
```

```bash
➜  interliaving-try python feed_session.py 
session_id: 913025dc-cec7-4150-9cf2-f8fc0ea583e6
snapshot_id: snap_shot_001
snapshot items: ['A1', 'B1', 'B2', 'A2', 'A3', 'B4', 'B3']

page1: ['A1', 'B1', 'B2']
next_cursor: 3

page2: ['A2', 'A3', 'B4']
next_cursor: 6

page3: ['B3']
next_cursor: None
```

FeedSessionStoreとして作成し、session_idとcursorを作成・保存するようにします。
次はsession_idのTTLを入れます。

```python
@dataclass
class FeedSession:
    session_id: str
    snapshot: Snapshot
    created_at: datetime
    expires_at: datetime

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
    
```

```bash
➜  interliaving-try python ttl_session.py 
session_id: ee1f53c7-61fe-4408-a6e4-799960d69271
snapshot_id: 2026-06-14 15:04:49.802405+00:00
expired_at: 2026-06-14 15:04:59.802405+00:00
is_expired: False

page1: ['A1', 'B1', 'B2']
next_cursor: 3

page2: ['A2', 'A3', 'B4']
next_cursor: 6

future_time: 2026-06-14 15:05:00.802405+00:00
is_expired after future_time: True
```

expires_atを定義することでセッションの期限を管理できる。
あえて期限を切らすことでどのようになるかコンソール結果から分かるようにした。
次はsessionの期限切れ時にsnapshotをrefreshする機能の追加をします。

```python
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

def get_page(store, session_id, cursor, ranking_a, ranking_b, limit, ttl_seconds=60, now=None):
    """
    session_idとcursorを使ってページを取得する。
    sessionが期限切れならsnapshotをrefreshする。
    """
    now = now or datetime.now(timezone.utc)
    session = store.get(session_id)

    if session_id is None:
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
```
```bash
➜  interliaving-try python refresh_snapshot.py
initial session_id: 5eebc30d-1d31-48a6-8444-2e46d6dd1867
initial snapshot_id: snap_shot_001
initial snapshot: ['A1', 'B1', 'B2', 'A2', 'A3', 'B4', 'B3']

page1: ['A1', 'B1', 'B2']
next_cursor: 3

page2: ['A2', 'A3', 'B4']
next_cursor: 6

after refresh snapshot_id: snap_shot_001
after refresh snapshot: ['A3', 'B4', 'A1', 'B1', 'A4', 'B6', 'B5', 'A2', 'A5', 'B7']
page after refresh: ['A3', 'B4', 'A1']
next_cursor: 3
```

全体のコードはリポジトリを参考にしてください。
refresh_session()とget_page()を追加しました。sessionの期限が切れて、新しいランキングが作り直されてsnapshotも作り直されています。
今はまだ表示が重複しているので、最後に表示が重複しないようにすれば今回の目的は達成です。

```python

```



## 今回の記事の参照先
- https://engineering.visional.inc/blog/615/implement-interleaving-for-search-evaluation/

- https://qiita.com/mpkato/items/99bd55cc17387844fd62

- https://www.nogawanogawa.com/entry/interleaving#Team-Draft-Interleaving
