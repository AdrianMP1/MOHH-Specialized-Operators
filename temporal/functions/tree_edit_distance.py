
from parser import Node, parse_expression

def tree_edit_distance(tree1, tree2):
    """
    Compare tree1 against tree2.
    """

    # Base cases
    if not tree1 and not tree2:
        return 0
    
    if not tree1:
        return sum(tree_edit_distance(None, child) for child in tree2.children) + 1
    
    if not tree2:
        return sum(tree_edit_distance(child, None) for child in tree1.children) + 1
    
    # Cost for substituting current nodparse_expressiones
    cost_substitution = 0 if tree1.value == tree2.value else 1

    # Initialize the DP table
    dp = [[0] * (len(tree2.children) + 1) for _ in range(len(tree1.children) + 1)]

    # Fill in the first row and column of the DP table (deletion/insertion)
    for i in range(1, len(tree1.children) + 1):
        dp[i][0] = dp[i-1][0] + tree_edit_distance(tree1.children[i-1], None)
    
    for j in range(1, len(tree2.children) + 1):
        dp[0][j] = dp[0][j-1] + tree_edit_distance(None, tree2.children[j-1])

    # Fill in the DP table
    for i in range(1, len(tree1.children) + 1):
        for j in range(1, len(tree2.children) + 1):
            cost_delete = dp[i-1][j] + tree_edit_distance(tree1.children[i-1], None)
            cost_insert = dp[i][j-1] + tree_edit_distance(None, tree2.children[j-1])
            cost_match = dp[i-1][j-1] + tree_edit_distance(tree1.children[i-1], tree2.children[j-1])
            dp[i][j] = min(cost_delete, cost_insert, cost_match)
    
    # Total cost includes the substitution of root nodes plus the edit distance of their subtrees
    return cost_substitution + dp[-1][-1]

if __name__ == "__main__":

    exp1 = "masked_cross(cos(x) + sin(y))"
    exp2 = "one_point(cos(x) + y)"

    treeA = parse_expression(exp1)
    treeB = parse_expression(exp2)

    #treeA = Node('A')
    #treeA.children = [Node('B'), Node('C')]

    #treeB = Node('X')
    #treeB.children = [Node('B')]

    print(tree_edit_distance(treeA, treeB))