# PCKP-Greedy
Greedy algorithm for a precedence-constrained knapsack problem, which is defined as a knapsack problem with an additional predecessor for each item, which has to be taken into the solution if the item is taken. If multiple items have the same predecessor, it only has to be chosen once.
If we have to items with the same profit to cost ratio, we want to take the one whose parent is already taken first.

# Setup
For usage, the package **anytree** is needed which can be installed with pip.

# Usage
The script only solves Precedence constraint knapsack problems having for each item only one predecessor.
As input two csv files are accepted, one contains the data for the weights and one contains the data for the value.
In each row, the last item precedence constraint for each item.
Furthermore one has to give the weight limit, which is hardcoded right now.
The output is a third csv which has entries equal to 1 for each item taken into the solution and 0 otherwise.

Make sure that if you want to change the name of the input files, you have to put the names into the code.
