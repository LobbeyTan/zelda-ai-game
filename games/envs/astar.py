from collections import namedtuple
Position = namedtuple("Position", ["x", "y"])
Move = namedtuple("Move", ["Position", "Value"])

class Segment:

    def __init__(self, length: int, position, parent= '', value = 0) -> None:
        self.parent = parent
        self.length = length
        self.value = value
        self.position = position

class Path:

    def __init__(self, segments) -> None:
        self.segments = segments

    def getOri(self):
        if not self.segments:
            return []
        return [self.segments[-1].position.x, self.segments[-1].position.y]

    def getFirst(self):
        if not self.segments:
            return []
        return [self.segments[-2].position.x, self.segments[-2].position.y]

    def process(self):
        if not self.segments:
            return []
        return [[segment.position.x, segment.position.y] for segment in self.segments][::-1][2:-1]



class Astar:

    def getPossibleAdjacentNeighbour(self, position: Position):
        adjacent_neighbours = []
        if position.x - 1 >= 0 and self.map[position.y][position.x - 1] != 1:
            if self.isPossibleMoves(Position(x=position.x - 1, y=position.y)):
                adjacent_neighbours.append(Position(x=position.x - 1, y=position.y))
        if position.x + 1 < len(self.map[0]) and self.map[position.y][position.x + 1] != 1:
            if self.isPossibleMoves(Position(x=position.x + 1, y=position.y)):
                adjacent_neighbours.append(Position(x=position.x + 1, y=position.y))
        if position.y - 1 >= 0 and self.map[position.y - 1][position.x] != 1:
            if self.isPossibleMoves(Position(x=position.x, y=position.y - 1)):
                adjacent_neighbours.append(Position(x=position.x, y=position.y - 1))
        if position.y + 1 < len(self.map) and self.map[position.y + 1][position.x] != 1:
            if self.isPossibleMoves(Position(x=position.x, y=position.y + 1)):
                adjacent_neighbours.append(Position(x=position.x, y=position.y + 1))
        return adjacent_neighbours

    def getAdjacentNeighbour(self, position: Position):
        adjacent_neighbours = []
        if position.x - 1 >= 0 and self.map[position.y][position.x - 1] != 1 and self.map[position.y][position.x - 1] != 2:
            adjacent_neighbours.append(Position(x=position.x - 1, y=position.y))
        if position.x + 1 < len(self.map[0]) and self.map[position.y][position.x + 1] != 1 and self.map[position.y][position.x + 1] != 2:
            adjacent_neighbours.append(Position(x=position.x + 1, y=position.y))
        if position.y - 1 >= 0 and self.map[position.y - 1][position.x] != 1 and self.map[position.y - 1][position.x] != 2:
            adjacent_neighbours.append(Position(x=position.x, y=position.y - 1))
        if position.y + 1 < len(self.map) and self.map[position.y + 1][position.x] != 1 and self.map[position.y + 1][position.x] != 2:
            adjacent_neighbours.append(Position(x=position.x, y=position.y + 1))
        return adjacent_neighbours

    def isPossibleMoves(self, move: Position):
        move_neighbours = self.getAdjacentNeighbour(move)
        for move_neighbour in move_neighbours:
            if self.map[move_neighbour.y][move_neighbour.x] > 4:
                return False
        return True

    def getDistance(self, start: Position, target: Position):
        return abs(start.x - target.x) + abs(start.y - target.y)
        
    def __init__(self, maP) -> None:
        self.orimap = maP
        self.map = self.orimap.tolist()

    def getPath(self, open_segment, open_value, target, player):
        # Initialize close list
        closed_segment = []

        while open_segment:
            print(len(open_segment))
            if len(open_segment) > 2000:
                return []
            current_segment_index = open_value.index(min(open_value))
            current_segment = open_segment.pop(current_segment_index)
            current_value = open_value.pop(current_segment_index)
            closed_segment.append(current_segment)
            # print(len(open_segment))
            # print((self.getDistance(target, player)) * 2)
            # if len(open_segment) > (self.getDistance(target, player) * 2):
            #     break

            # Found the target
            if current_segment.position == target:
                path_segments = []
                while current_segment:
                    path_segments.append(current_segment)
                    current_segment = current_segment.parent
                return path_segments
            
            # Get current segment's adjacent neighbour
            # valid = True
            # adjacent_neighbours = self.getAdjacentNeighbour(current_segment.position)
            # for adjacent_neighbour in adjacent_neighbours:
            #     if self.map[adjacent_neighbour.y][adjacent_neighbour.x] > 4:
            #         valid = False
            
            # if not valid:
            #     continue

            if self.map[current_segment.position.y][current_segment.position.x] > 4:
                continue
            
            possible_moves = self.getAdjacentNeighbour(current_segment.position)
            for possible_move in possible_moves:
                skip = False
                segment = Segment(position=possible_move, parent=current_segment, length=current_segment.length + 1, value=current_segment.length + self.getDistance(start=possible_move,target=target))
                for close_segmenT in closed_segment:
                    if close_segmenT.position == segment.position:
                        skip = True
                        break
                
                if skip:
                    continue

                for open_segmenT in open_segment:
                    if open_segmenT.position == segment.position:
                        if open_segmenT.value < segment.value:
                            skip = True
                            break
                
                if skip:
                    continue

                open_segment.append(segment)
                open_value.append(segment.value)  
        return []

    def getNextMove(self):
        door = 0
        key = 0

        # Get the position for Player, Key and Door
        for i in range(len(self.map)):
            if 2 in self.map[i]:
                player = Position(y=i, x=self.map[i].index(2))
            if 3 in self.map[i]:
                key = Position(y=i, x=self.map[i].index(3))
            if 4 in self.map[i]:
                door = Position(y=i, x=self.map[i].index(4))
        # Set the target
        if key != 0:
            target = key
        else:
            target = door
        
        # Get starting possible move
        starting_possible_moves = self.getPossibleAdjacentNeighbour(player)

        # Initialize open list for A* search
        parent = Segment(position=player, length=0)
        open_segment = [Segment(position=x, parent=parent, value=self.getDistance(start=x,target=target), length=1) for x in starting_possible_moves]
        open_value = [x.value for x in open_segment]

        # Get the path to target
        path = Path(self.getPath(open_segment, open_value, target, player))

        return path.getOri(), path.getFirst(), path.process()

    def step(self):
        player_ori, player_next, path = self.getNextMove()
        if player_ori == []:
            return
        self.orimap[player_ori[1]][player_ori[0]] = 0
        self.orimap[player_next[1]][player_next[0]] = 2

        for p in path:
             self.orimap[p[1]][p[0]] = 8
    


    