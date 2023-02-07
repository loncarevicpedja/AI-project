from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
import heapq
from collections import deque
from queue import PriorityQueue

def depth_first_search(matrix, prices, start, goal):
    visited = set()
    queue = deque([(start, [start], 0)])
    while queue:
        pos, path, cost = queue.popleft()
        if pos in visited:
            continue
        visited.add(pos)
        if pos == goal:
            return path, cost
        neighbors = get_neighbors(matrix, pos)
        neighbors.sort(key=lambda x: (prices[matrix[x[0]][x[1]]], (x[0]-pos[0], x[1]-pos[1])))
        for neighbor in neighbors:
            if neighbor not in visited:
                cost_to_neighbor = prices[matrix[neighbor[0]][neighbor[1]]]
                queue.append((neighbor, path + [neighbor], cost + cost_to_neighbor))
    return None, None

def breadth_first_search(matrix, prices, start, goal):
    visited = set()
    queue = deque([(start, [start], 0)])
    while queue:
        pos, path, cost = queue.popleft()
        if pos in visited:
            continue
        visited.add(pos)
        if pos == goal:
            return path, cost
        neighbors = get_neighbors(matrix, pos)
        neighbors.sort(key=lambda x: (average_cost(matrix, prices, x), (x[0]-pos[0], x[1]-pos[1])))
        for neighbor in neighbors:
            if neighbor not in visited:
                cost_to_neighbor = prices[matrix[neighbor[0]][neighbor[1]]]
                queue.append((neighbor, path + [neighbor], cost + cost_to_neighbor))
    return None, None

def average_cost(matrix, prices, pos):
    neighbors = get_neighbors(matrix, pos)
    total_cost = 0
    for neighbor in neighbors:
        total_cost += prices[matrix[neighbor[0]][neighbor[1]]]
    return total_cost / len(neighbors)

def branch_and_bound(matrix, prices, start, goal):
    visited = set()
    queue = PriorityQueue()
    queue.put((0, [start]))
    while not queue.empty():
        path = queue.get()[1]
        pos = path[-1]
        if pos in visited:
            continue
        visited.add(pos)
        if pos == goal:
            return path, sum(prices[matrix[x[0]][x[1]]] for x in path)
        neighbors = get_neighbors(matrix, pos)
        for neighbor in neighbors:
            if neighbor not in visited:
                cost = prices[matrix[neighbor[0]][neighbor[1]]]
                estimated_cost = sum(prices[matrix[x[0]][x[1]]] for x in path) + cost
                queue.put((estimated_cost, path + [neighbor]))
    return None, None

def a_star(matrix, prices, start, goal):
    heap = [(0, start)]
    visited = set()
    path_cost = {start: 0}
    path = {start: [start]}
    while heap:
        (cost, curr) = heapq.heappop(heap)
        if curr in visited:
            continue
        visited.add(curr)
        if curr == goal:
            return path[curr], cost
        for neighbor in get_neighbors(matrix, curr):
            if neighbor in visited:
                continue
            cost_to_neighbor = prices[matrix[neighbor[0]][neighbor[1]]]
            new_cost = cost + cost_to_neighbor
            if neighbor not in path_cost or new_cost < path_cost[neighbor]:
                manhattan_distance = abs(neighbor[0]-goal[0]) + abs(neighbor[1]-goal[1])
                priority = new_cost + manhattan_distance
                path_cost[neighbor] = new_cost
                path[neighbor] = path[curr] + [neighbor]
                heapq.heappush(heap, (priority, neighbor))
    return None, None

def manhattan(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)

def get_neighbors(matrix, pos):
    rows = len(matrix)
    cols = len(matrix[0])
    row, col = pos
    neighbors = []
    if row > 0:
        neighbors.append((row-1, col))
    if col < cols-1:
        neighbors.append((row, col+1))
    if row < rows-1:
        neighbors.append((row+1, col))
    if col > 0:
        neighbors.append((row, col-1))
    return neighbors


@api_view(['POST'])

def solve(request):
    data = json.loads(request.body)
    tiles = data['tiles']
    playerx = data['playery']
    playery = data['playerx']
    destinationx = data['destinationy']
    destinationy = data['destinationx']

    matrix = []
    for i in range(data['size']):
        matrix.append(tiles[i * data['size']:i * data['size'] +   data['size']])
    print(matrix)
    agentPosition = []
    agentPosition = playerx, playery
    tAgentPosition = tuple(agentPosition)
    print(tAgentPosition)
    finishPosition = []
    finishPosition = destinationx, destinationy
    tFinishPosition = tuple(finishPosition)
    print(tFinishPosition)
    agent = data["player_type"] 
    prices = {'r': 2, 'g': 3, 'm': 5, 'd': 7, 'w': 500, 's' : 1000}
    

    if agent == 1:
        path, cost = depth_first_search(matrix, prices, tAgentPosition, tFinishPosition)
    elif agent == 2:
        path, cost = breadth_first_search(matrix, prices, tAgentPosition, tFinishPosition)
    elif agent == 3:
        path, cost = branch_and_bound(matrix, prices, tAgentPosition, tFinishPosition)
    elif agent == 4:
        path, cost = a_star(matrix, prices, tAgentPosition, tFinishPosition)
    data = {
        "tiles" : path,
        "price" : cost
    }

    print("PRICE:", data["price"])
    print("PATH:", data["tiles"])

    # neighbors = get_neighbors(matrix, (0, 0))
    # neighbors.sort(key=lambda x: (prices[matrix[x[0]][x[1]]], abs(x[0]-x[0])+ abs(x[1]-x[1])))
    # lowest_price_neighbor = neighbors[0]
    # print(f'({lowest_price_neighbor[0]}, {lowest_price_neighbor[1]}) - {prices[matrix[lowest_price_neighbor[0]][lowest_price_neighbor[1]]]}')


    return Response(data)