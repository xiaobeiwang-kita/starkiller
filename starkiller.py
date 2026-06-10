from functools import lru_cache
lastscore = int(input("请输入当前分数："))
# encode colors chars: Y,G,B,R,P
top = [
    list("YPBBYBYRRB"),
    list("RGGPGYGYYB"),
    list("PGBPYYBPBB"),
    list("GRGYYPYBBR"),
    list("YYPBYRPGRG"),
    list("YGGPYGBYRG"),
    list("RRYPGPGPGY"),
    list("PPGBPPRRYG"),
    list("BPGRGRRPGR"),
    list("RYYRYPRYYB"),
]
# use columns bottom-up
H=10; W=10
cols=[]
for c in range(W):
    col=[]
    for r in range(H-1,-1,-1): col.append(top[r][c])
    cols.append(tuple(col))
state=tuple(cols)
def groups(state):
    seen=set(); res=[]
    for x,col in enumerate(state):
        for y,val in enumerate(col):
            if (x,y) in seen: continue
            # bfs
            stack=[(x,y)]; seen.add((x,y)); cells=[]
            while stack:
                a,b=stack.pop(); cells.append((a,b))
                for da,db in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx,ny=a+da,b+db
                    if 0<=nx<len(state) and 0<=ny<len(state[nx]) and (nx,ny) not in seen and state[nx][ny]==val:
                        seen.add((nx,ny)); stack.append((nx,ny))
            if len(cells)>=2:
                res.append((val,cells))
    return res
def remove(state, cells):
    rem=set(cells); new=[]
    for x,col in enumerate(state):
        nc=tuple(v for y,v in enumerate(col) if (x,y) not in rem)
        if nc: new.append(nc)
    return tuple(new)
def score_group(n): return 5*n*n
def rem_count(state): return sum(len(c) for c in state)
def bonus(state):
    m=rem_count(state)
    return max(0, 2000-20*m*m) if m<10 else 0  # assume
def canon_move(cells):
    # choose lowest then left? return bottom-up row,col of one cell before move
    return min(((y+1,x+1) for x,y in cells)) # bottom-up row, col
print(len(groups(state)), [(v,len(c),canon_move(c)) for v,c in groups(state)[:10]])
print(rem_count(state)) 

from heapq import nlargest



COLOR_NAME = {
    "Y": "黄色",
    "G": "绿色",
    "B": "蓝色",
    "R": "红色",
    "P": "粉色",
}

def beam_search(width=50000, depth_limit=100):
    beam = [(0, state, [])]
    best = (0, state, [])

    for d in range(depth_limit):
        cand = []

        for sc, st, path in beam:
            gs = groups(st)

            if not gs:
                total = sc + bonus(st)
                if total > best[0]:
                    best = (total, st, path + [("bonus", bonus(st), rem_count(st))])
                continue

            for val, cells in gs:
                n = len(cells)
                ns = remove(st, cells)
                nsc = sc + score_group(n)

                h = nsc + bonus(ns) + 2 * sum(len(c) ** 2 for c in ns)
                cand.append((h, nsc, ns, path + [(val, n, canon_move(cells))]))

        if not cand:
            break

        cand = nlargest(width, cand, key=lambda x: x[0])
        beam = [(nsc, ns, path) for h, nsc, ns, path in cand]

        for h, nsc, ns, path in cand[:100]:
            if not groups(ns):
                total = nsc + bonus(ns)
                if total > best[0]:
                    best = (total, ns, path + [("bonus", bonus(ns), rem_count(ns))])

    return best, beam


best, beam = beam_search(50000)

print("\n========== 最佳路线 ==========\n")

st = state
added_score = 0
current_score = lastscore

for i, (val, n, coord) in enumerate([m for m in best[2] if m[0] != "bonus"], 1):
    row, col = coord
    y, x = row - 1, col - 1

    cell = None
    for v, cells in groups(st):
        if (x, y) in cells:
            cell = (v, cells)
            break

    if cell is None:
        raise ValueError(f"第{i}步找不到对应色块：row {row}, col {col}")

    step_score = score_group(len(cell[1]))
    added_score += step_score
    current_score += step_score

    print(
        f"第{i}步：点{COLOR_NAME[val]}，"
        f"第{row}行第{col}列，"
        f"消{len(cell[1])}个，"
        f"+{step_score}分，"
        f"当前总分 {current_score}"
    )

    st = remove(st, cell[1])

end_bonus = bonus(st)
current_score += end_bonus

print("\n========== 结算 ==========\n")
print(f"剩余星星：{rem_count(st)} 个")
print(f"剩余奖励：+{end_bonus} 分")
print(f"本关新增：+{added_score + end_bonus} 分")
print(f"最终总分：{current_score} 分")