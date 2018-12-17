# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 19:16:13 2018

@author: Matthias Bischof
"""

import anytree
import csv

# Only supports one precedence constraint for each node

class CSVReader(object):
    # Reads out CSV files formatted as a matrices: one for costs, one for profits
    def __init__(self, cost_filename = 'cost.csv', profit_filename='profit.csv'):
        self.cost_filename = cost_filename
        self.profit_filename = profit_filename
        self.costs = self.open_csv(self.cost_filename)
        self.profits = self.open_csv(self.profit_filename)

    def open_csv(self, filename):
        i = 0
        lst = list()
        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';')
            for row in csvreader:
                transf_row = [tup for tup in zip(row, range(len(row)))]
                lst.append((transf_row, i))
                i+=1
        return lst

    def create_tree(self):
        # Transforms the matrices into Tree nodes consisting of an index, cost, profit and the coordinates in the original csv
        i = 0
        root = TKPTreeNode(i, None, 0, 0, x=None, y=None)
        node_lst = [root]
        for cost_tup, profit_tup in zip(self.costs, self.profits):
            i += 1
            necessary_tup = [cost_tup[0].pop(), profit_tup[0].pop()]
			# define the precedence constraint as a tree node
            subproblem = TKPTreeNode(id=i, parent=root,
                                     cost=int(necessary_tup[0][0]), 
                                     profit=int(necessary_tup[1][0]), 
                                     x=len(cost_tup[0]), y=cost_tup[1])
            node_lst.append(subproblem)
			# define the other nodes in that row as children of the constraint above
            for cost_item, profit_item in zip(cost_tup[0], profit_tup[0]):
                i += 1
                node_lst.append(TKPTreeNode(id=i, parent=subproblem, cost=int(cost_item[0]), profit=int(profit_item[0]), x=cost_item[1], y=cost_tup[1]))
        return node_lst


class TKPTreeNode(anytree.Node):
    def __init__(self, id, parent, cost, profit, x, y):
            super().__init__(id, parent)
            self.cost = cost
            self.profit = profit
            self.set_profit_idx()
            self.set = 0
            self.set_all_cost()
            self.x = x
            self.y = y

    def set_profit_idx(self):
        # profit to cost ratio
        try:
            self.profit_index = self.profit / self.cost
        except ZeroDivisionError:
            self.profit_index = 0

    def set_all_cost(self):
        # Take the cost of the parent into the childs cost. Thus we can assure, that while 
        # having two children with the same ratio, we take the one whose parent is already taken.
        try:
            self.cost = self.cost + self.parent.cost
        except:
            self.cost = 0

class Solver_dynamic(object):
    def __init__(self, tkp_root, bound):
        self.tree = tkp_root
        self.bound = bound
        self.weight = 0 
        self.items = list()
        self.solution_profit = 0

    def knapsack(self):
        # Puts in each iteration item with the highest ratio of profit to cost
        # into the solution set. When capacity is reached, it tries the next
        # worse item.
        while True:
            # Take all nodes that come into question
            all_nodes = [subnode for subnode in self.tree.descendants 
                         if subnode.set == 0 and subnode.profit > 0]
            if not all_nodes:
                # No nodes left
                break
            # Choose node with the best profit to cost ratio
            best_item = sorted(all_nodes, key=lambda x:x.profit_index)[-1]
            self.add_item(best_item)
            w = sum([node.cost for node in self.items])
            # Check that the weight does not exceed the limit
            if w > self.bound:
                # If the limit is exceeded, throw the item away
                self.delete_item(best_item)
                self.items.remove(best_item)
            else:
                # Adjust the solution weight
                self.weight = w
        self.solution_profit = sum([node.profit for node in self.items])
        return (self.weight, self.solution_profit, self.items)

    def add_item(self, item):
        # Adds an item to the solution
        item.set = 1
        self.items.append(item)
        # Check if the precedence constraint is satisfied
        if item.parent.set < 1:
            item.cost = item.cost - item.parent.cost
            self.items.append(item.parent)
            item.parent.set = 1
            for node in item.siblings:
                # Remove parent cost from children
                node.cost = node.cost - item.parent.cost
                node.set_profit_idx()

    def delete_item(self, item):
        lst = [node for node in item.siblings if node.set == 1]
        if not lst:
            item.parent.set = 0
            self.items.remove(item.parent)
            for node in item.siblings:
                # Add the weight of the constraint to each sibling of item 
                # It makes profit to cost ratio worse
                node.cost = node.cost + node.parent.cost
        item.set = -1

class CSVWriter(object):
    # Writes the solution into a CSV file. Same format as the input files, 
    #for each item being taken, set cell to 1, 0 otherwise
    def __init__(self, solution, tkp_root):
        self.solution_cost = solution[0]
        self.solution_profit = solution[1]
        self.node_lst = solution[2]
        self.tkp_root = tkp_root
        self.generate_matrix()

    def generate_matrix(self):
        # solution matrix 
        self.matrix = [
                  [0] +
                  [0 for leaf in subproblem_node.children]
                   for subproblem_node in tkp_root.children
                   ]
        for n in self.node_lst:
            self.matrix[n.y][n.x] = 1

    def write_csv(self):
        with open('solution.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            for row in self.matrix:
                csvwriter.writerow(row)
            csvwriter.writerow(['Cost:', self.solution_cost])
            csvwriter.writerow(['Profit:', self.solution_profit])

if __name__ == "__main__":
    csvread = CSVReader()
    node_lst = csvread.create_tree()
    tkp_root = node_lst[0]
    solver = Solver_dynamic(tkp_root, 30)
    solution = solver.knapsack()
    csvwrite = CSVWriter(solution, tkp_root)
    csvwrite.write_csv()
            