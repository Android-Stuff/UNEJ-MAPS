from flask import Flask, jsonify, request, send_file, render_template
import heapq
from collections import deque

app = Flask(__name__)

NODES = [
    {'id': 'rektorat', 'label': 'Rektorat', 'lat': -8.165048399810725, 'lng': 113.71630295832149},
    {'id': 'library', 'label': 'Perpustakaan', 'lat': -8.165488, 'lng': 113.7173286},
    {'id': 'fasilkom', 'label': 'Fasilkom', 'lat': -8.1657613, 'lng': 113.7170154},
    {'id': 'masjid', 'label': 'Masjid', 'lat': -8.1639625, 'lng': 113.7150476},
    {'id': 'fkip', 'label': 'Fak. FKIP', 'lat': -8.166694185407048, 'lng': 113.71580935809783},
    {'id': 'fmipa', 'label': 'FMIPA', 'lat': -8.164200657427571, 'lng': 113.71789928525561},
    {'id': 'auditorium', 'label': 'Gedung Auditorium', 'lat': -8.163805199100688, 'lng': 113.71400522654248},
    {'id': 'soetardjo', 'label': 'Gedung Soetardjo', 'lat': -8.164949491951655, 'lng': 113.71263148549767},
    {'id': 'fk', 'label': 'Fakultas Kedokteran', 'lat': -8.16135798215189, 'lng': 113.71836289288191},
    {'id': 'ftek', 'label': 'Fakultas Teknik', 'lat': -8.162188934459389, 'lng': 113.72090327504522}
]

EDGES = [
    {'from': 'rektorat', 'to': 'library', 'w': 2},
    {'from': 'rektorat', 'to': 'masjid', 'w': 3},
    {'from': 'rektorat', 'to': 'fkip', 'w': 3},
    {'from': 'library', 'to': 'fasilkom', 'w': 1},
    {'from': 'library', 'to': 'fmipa', 'w': 2},
    {'from': 'masjid', 'to': 'auditorium', 'w': 3},
    {'from': 'fasilkom', 'to': 'rektorat', 'w': 2},
    {'from': 'auditorium', 'to': 'soetardjo', 'w': 2},
    {'from': 'fkip', 'to': 'soetardjo', 'w': 4},
    {'from': 'fmipa', 'to': 'fk', 'w': 4},
    {'from': 'fmipa', 'to': 'ftek', 'w': 5},
    {'from': 'fk', 'to': 'ftek', 'w': 4},
    {'from': 'fkip', 'to': 'fasilkom', 'w': 3}
]

graph = {n['id']: [] for n in NODES}
node_map = {n['id']: n for n in NODES}
for e in EDGES:
    graph[e['from']].append({'to': e['to'], 'w': e['w']})
    graph[e['to']].append({'to': e['from'], 'w': e['w']})

# FUNCTIONS

def dijkstra(src, dst):
    dist = {n['id']: float('inf') for n in NODES}
    prev = {n['id']: None for n in NODES}
    visited = set()
    log = []
    
    dist[src] = 0
    pq = [(0, src)]
    
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        log.append(f"Kunjungi: {node_map[u]['label']}")
        
        if u == dst:
            break
            
        for edge in graph[u]:
            to, w = edge['to'], edge['w']
            alt = dist[u] + w
            if alt < dist[to]:
                dist[to] = alt
                prev[to] = u
                heapq.heappush(pq, (alt, to))
                
    path = []
    cur = dst
    while cur:
        path.insert(0, cur)
        cur = prev[cur]
        
    return {"path": path if path and path[0] == src else [], "dist": dist[dst], "log": log}

def bfs(src, dst):
    queue = deque([[src]])
    visited = {src}
    log = []
    
    while queue:
        path = queue.popleft()
        u = path[-1]
        log.append(f"Kunjungi: {node_map[u]['label']}")
        
        if u == dst:
            return {"path": path, "dist": len(path) - 1, "log": log}
            
        for edge in graph[u]:
            to = edge['to']
            if to not in visited:
                visited.add(to)
                queue.append(path + [to])
                
    return {"path": [], "dist": "Infinity", "log": log}

def dfs(src, dst):
    log = []
    found = None
    
    def dfs_r(node, path, visited):
        nonlocal found
        if found:
            return
        visited.add(node)
        log.append(f"Jelajahi: {node_map[node]['label']}")
        
        if node == dst:
            found = list(path)
            return
            
        for edge in graph[node]:
            to = edge['to']
            if to not in visited:
                dfs_r(to, path + [to], visited)

    dfs_r(src, [src], set())
    return {"path": found if found else [], "dist": len(found) - 1 if found else "Infinity", "log": log}

# ROUTING API

@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/api/route', methods=['POST'])
def find_route():
    data = request.json
    src = data.get('from')
    dst = data.get('to')
    algo = data.get('algo', 'dijkstra')
        
    if algo == 'dijkstra':
        result = dijkstra(src, dst)
    elif algo == 'bfs':
        result = bfs(src, dst)
    elif algo == 'dfs':
        result = dfs(src, dst)
        
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)