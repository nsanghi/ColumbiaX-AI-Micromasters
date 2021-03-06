import time
import argparse
import sys
from collections import deque
import os


class Directions:

    UP = 'Up'
    DOWN = 'Down'
    LEFT = 'Left'
    RIGHT = 'Right'
    ALL_MOVES = [UP, DOWN, LEFT, RIGHT]

class PriorityQueue:

    def __init__(self):
        import itertools
        self.pq = []  # list of entries arranged in a heap
        self.entry_finder = {}  # mapping of tasks to entries
        self.REMOVED = '<removed-task>'  # placeholder for a removed task
        self.counter = itertools.count()  # unique sequence count

    def add_task(self, task, priority=0):
        import itertools
        from heapq import heappush
        # Add a new task or update the priority of an existing task
        if task in self.entry_finder:
            self.remove_task(task)
        self.count = next(self.counter)
        entry = [priority, self.count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)

    def remove_task(self, task):
        # Mark an existing task as REMOVED.  Raise KeyError if not found.
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop_task(self):

        from heapq import heappop

        # Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')

    def has_task(self, task):
        return task in self.entry_finder

    def is_not_empty(self):
        return len(self.pq) > 0

    def size(self):
        return len(self.pq)



class State:

    def __init__(self, state, parent, move, path_cost):
        self.state = state
        self.parent = parent
        self.move_frm_parent = move
        self.path_cost = path_cost

    def is_goal_state(self):
        return self.state == GOAL


    def __eq__(self, other):
        if other == None:
            return False
        if not self.state == other.state:
            return False
        return True

    def __hash__(self):
        return hash(self.state)

    def __str__(self):
        return self.state.__str__()+ 'AND Path Cost:{}'.format(self.path_cost)

    def __unicode__(self):
        return self.state.__unicode__() + 'AND Path Cost:{}'.format(self.path_cost)

    def __repr__(self):
        return self.state.__repr__() + 'AND Path Cost:{}'.format(self.path_cost)

    def __cmp__(self, other):
        if other == None or isinstance(other, State):
            raise KeyError('objects being comapred below to different classes')
        return self.state < other.state


    def get_legal_moves(self):

        legal_moves = []
        n = int(len(self.state)**0.5)
        blank_pos = self.state.index(0)

        for d in Directions.ALL_MOVES:

            # for UP to be legal, blank should not be in top row
            if d == Directions.UP and blank_pos >= n:
                legal_moves.append(d)

            # for DOWN to be legal, blank should not be in last row
            if d == Directions.DOWN and blank_pos < n**2 - n:
                legal_moves.append(d)

            # for LEFT to be legal, blank should not be in left column
            if d == Directions.LEFT and not blank_pos % n == 0:
                legal_moves.append(d)

            # for RIGHT to be legal, blank should not in right column
            if d == Directions.RIGHT and not blank_pos % n ==  n-1:
                legal_moves.append(d)

        return legal_moves

    def neighbors(self):
        result = []
        legal_moves = self.get_legal_moves()

        for d in legal_moves:
            new_state = list(self.state)
            n = int(len(self.state) ** 0.5)
            blank_pos = self.state.index(0)
            # find the new position for blank based on move
            if d == Directions.UP:
                new_blank_pos = blank_pos - n
            elif d == Directions.DOWN:
                new_blank_pos = blank_pos + n
            elif d == Directions.LEFT:
                new_blank_pos = blank_pos - 1
            elif d == Directions.RIGHT:
                new_blank_pos = blank_pos + 1
            else:
                raise ValueError('Should never come here')

            new_state[blank_pos] = new_state[new_blank_pos]
            new_state[new_blank_pos] = 0

            result.append(State(tuple(new_state), self, d, self.path_cost+1))

        return result


    def manhattan_dis(self):
        n = int(len(self.state) ** 0.5)
        dis = 0
        for i in range(n):
            if self.state[i] != 0: # i.e. the position i does not contain blank "0"
                #  add manhattan dist i.e. (offset in no. of rows + offset in no. of columns)
                dis += abs(self.state[i] - i) / n + abs(self.state[i] - i) % n

        return dis


def bfs(initial_state):

    # start time
    st_time = time.clock()

    # node will have (board, depth)
    frontier = deque([initial_state])
    # to have efficinet way to check for existence of a state in frontier
    visited_states = set()
    visited_states.add(initial_state)
    nodes_expanded = 0
    max_fringe_size = -1
    max_search_depth = -1

    while len(frontier) > 0:
        node = frontier.popleft()

        if node.is_goal_state():
            # return (path to goal, cost_of_path, nodes expanded, fringe_size
            path_to_goal = []
            cur_state = node
            while cur_state.parent:
                path_to_goal.append(cur_state.move_frm_parent)
                cur_state = cur_state.parent
            path_to_goal = path_to_goal[::-1]
            cost_of_path = len(path_to_goal)
            fringe_size = len(frontier)
            search_depth = node.path_cost
            runtime = time.clock() - st_time
            if not os.name == 'nt':
                import resource
                max_ram_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss # get ru_maxrss
            else:
                max_ram_usage = None

            write_output(path_to_goal, cost_of_path, nodes_expanded, fringe_size, max_fringe_size,
                         search_depth, max_search_depth, runtime, max_ram_usage)
            return

        # the node out of queue is not a goal and we need to expand it
        nodes_expanded += 1

        for neighbor in node.neighbors():
            if not neighbor in visited_states:
                frontier.append(neighbor)
                visited_states.add(neighbor)
                max_fringe_size = max(max_fringe_size, len(frontier))
                max_search_depth = max(max_search_depth, neighbor.path_cost)

    print("ERROR: bfs should never reach this point")

def dfs(initial_state):

    # start time
    st_time = time.clock()

    # node will have (board, depth)
    frontier = deque([initial_state])
    # to have efficinet way to check for existence of a state in frontier
    visited_states = set()
    visited_states.add(initial_state)
    nodes_expanded = 0
    max_fringe_size = -1
    max_search_depth = -1

    while len(frontier) > 0:
        node = frontier.pop()

        if node.is_goal_state():
            # return (path to goal, cost_of_path, nodes expanded, fringe_size
            path_to_goal = []
            cur_state = node
            while cur_state.parent:
                path_to_goal.append(cur_state.move_frm_parent)
                cur_state = cur_state.parent
            path_to_goal = path_to_goal[::-1]
            cost_of_path = len(path_to_goal)
            fringe_size = len(frontier)
            search_depth = node.path_cost
            runtime = time.clock() - st_time
            if not os.name == 'nt':
                import resource
                max_ram_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss # get ru_maxrss
            else:
                max_ram_usage = None

            write_output(path_to_goal, cost_of_path, nodes_expanded, fringe_size, max_fringe_size,
                     search_depth, max_search_depth, runtime, max_ram_usage)
            return

        # the node out of queue is not a goal and we need to expand it
        nodes_expanded += 1
        #print(nodes_expanded)

        ## for dfs we need to reverse the neighbour list before inserstion so
        # that popping will result in UDLR order
        for neighbor in node.neighbors()[::-1]:

            if not neighbor in visited_states:
                frontier.append(neighbor)
                visited_states.add(neighbor)
                max_fringe_size = max(max_fringe_size, len(frontier))
                max_search_depth = max(max_search_depth, neighbor.path_cost)

    print("ERROR: dfs should never reach this point")


def ast(initial_state):

    # start time
    st_time = time.clock()

    # for A star frontier is a priority queue with ability
    # to modify task priority in place
    frontier = PriorityQueue()
    manhat_dis = initial_state.manhattan_dis()
    # node will have (board, depth/path_cost - i.e. g(n))
    frontier.add_task(initial_state, manhat_dis)

    # to have efficinet way to check for existence of a state in frontier
    explored_states = set()
    nodes_expanded = 0
    max_fringe_size = -1
    max_search_depth = -1

    while frontier.is_not_empty() > 0:

        node = frontier.pop_task()
        explored_states.add(node)

        if node.is_goal_state():
            # return (path to goal, cost_of_path, nodes expanded, fringe_size
            path_to_goal = []
            cur_state = node
            while cur_state.parent:
                path_to_goal.append(cur_state.move_frm_parent)
                cur_state = cur_state.parent
            path_to_goal = path_to_goal[::-1]
            cost_of_path = len(path_to_goal)
            fringe_size = frontier.size()
            search_depth = node.path_cost
            runtime = time.clock() - st_time
            if not os.name == 'nt':
                import resource
                max_ram_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss # get ru_maxrss
            else:
                max_ram_usage = None

            write_output(path_to_goal, cost_of_path, nodes_expanded, fringe_size, max_fringe_size,
                     search_depth, max_search_depth, runtime, max_ram_usage)
            return

        # the node out of queue is not a goal and we need to expand it
        nodes_expanded += 1
        #print(nodes_expanded)

        for neighbor in node.neighbors():

            if not (neighbor in explored_states or frontier.has_task(neighbor)):
                frontier.add_task(neighbor, neighbor.path_cost + neighbor. manhattan_dis())
                max_fringe_size = max(max_fringe_size, frontier.size())
                max_search_depth = max(max_search_depth, neighbor.path_cost)
            elif frontier.has_task(neighbor):
                frontier.remove_task(neighbor)
                frontier.add_task(neighbor, neighbor.path_cost + neighbor. manhattan_dis())

    print("ERROR: ast should never reach this point")


def ida_search(node, bound, st_time, nodes_expanded, max_fringe_size, max_search_depth):

    # to keep the minum of values that crossed current bound
    min_above_bound = float('inf')

    frontier = deque([node])
    # to have efficinet way to check for existence of a state in frontier
    visited_states = set()
    visited_states.add(node)

    while len(frontier) > 0:
        node = frontier.pop()

        if node.is_goal_state():
            # return (path to goal, cost_of_path, nodes expanded, fringe_size
            path_to_goal = []
            cur_state = node
            while cur_state.parent:
                path_to_goal.append(cur_state.move_frm_parent)
                cur_state = cur_state.parent
            path_to_goal = path_to_goal[::-1]
            cost_of_path = len(path_to_goal)
            fringe_size = len(frontier)
            search_depth = node.path_cost
            runtime = time.clock() - st_time
            if not os.name == 'nt':
                import resource
                max_ram_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss # get ru_maxrss
            else:
                max_ram_usage = None

            write_output(path_to_goal, cost_of_path, nodes_expanded, fringe_size, max_fringe_size,
                     search_depth, max_search_depth, runtime, max_ram_usage)

            return 'FOUND', bound, nodes_expanded, max_fringe_size, max_search_depth

        # the node out of queue is not a goal and we need to expand it
        nodes_expanded += 1
        #print(nodes_expanded)

        ## for dfs we need to reverse the neighbour list before inserstion so
        # that popping will result in UDLR order
        for neighbor in node.neighbors()[::-1]:

            if not neighbor in visited_states:
                cost = neighbor.path_cost + neighbor.manhattan_dis()
                if  cost <= bound:
                    frontier.append(neighbor)
                    visited_states.add(neighbor)
                    max_fringe_size = max(max_fringe_size, len(frontier))
                    max_search_depth = max(max_search_depth, neighbor.path_cost)
                else:
                    min_above_bound = min(min_above_bound, cost)

    return 'NOT_FOUND', min_above_bound, nodes_expanded, max_fringe_size, max_search_depth


def ida(initial_state):

    # start time
    st_time = time.clock()
    bound = initial_state.manhattan_dis()
    nodes_expanded = 0
    max_fringe_size = -1
    max_search_depth = -1

    while True:
        status, bound, nodes_expanded, max_fringe_size, max_search_depth = \
            ida_search(initial_state, bound, st_time, nodes_expanded, max_fringe_size, max_search_depth)

        if status == 'FOUND':
            break

    print "IDA SOlved the problem"

def write_output(path_to_goal, cost_of_path, nodes_expanded, fringe_size,
                 max_fringe_size, search_depth, max_search_depth, runtime,
                 max_ram_usage):
    output = open('output.txt', 'w')
    output.write('path_to_goal: {}\n'.format(path_to_goal))
    output.write('cost_of_path: {}\n'.format(cost_of_path))
    output.write('nodes_expanded: {}\n'.format(nodes_expanded))
    output.write('fringe_size: {}\n'.format(fringe_size))
    output.write('max_fringe_size: {}\n'.format(max_fringe_size))
    output.write('search_depth: {}\n'.format(search_depth))
    output.write('max_search_depth: {}\n'.format(max_search_depth))
    output.write('running_time: {}\n'.format(runtime))
    output.write('max_ram_usage: {}'.format(max_ram_usage))
    output.close()


def read_command( argv ):

    parser = argparse.ArgumentParser(description='Run Search.')
    parser.add_argument('method', choices=['bfs', 'dfs', 'ast', 'ida'], help='type of search')
    parser.add_argument('state', type=lambda s: tuple([int(item) for item in s.split(',')]))
    return parser.parse_args(argv)


if __name__ == '__main__':
    args = read_command(sys.argv[1:])
    state = State(args.state, None, None, 0)
    method = args.method
    GOAL = tuple([i for i in range(len(state.state))])
    if method == 'bfs':
        bfs(state)
    elif method == 'dfs':
        dfs(state)
    elif method == 'ast':
        ast(state)
    elif method == 'ida':
        ida(state)


