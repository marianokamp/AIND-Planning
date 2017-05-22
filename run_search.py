import argparse
from timeit import default_timer as timer
from aimacode.search import InstrumentedProblem
from aimacode.search import (breadth_first_search, astar_search,
    breadth_first_tree_search, depth_first_graph_search, uniform_cost_search,
    greedy_best_first_graph_search, depth_limited_search,
    recursive_best_first_search)
from my_air_cargo_problems import air_cargo_p1, air_cargo_p2, air_cargo_p3

PROBLEM_CHOICE_MSG = """
Select from the following list of air cargo problems. You may choose more than
one by entering multiple selections separated by spaces.
"""

SEARCH_METHOD_CHOICE_MSG = """
Select from the following list of search functions. You may choose more than
one by entering multiple selections separated by spaces.
"""

INVALID_ARG_MSG = """
You must either use the -m flag to run in manual mode, or use both the -p and
-s flags to specify a list of problems and search algorithms to run. Valid
choices for each include:
"""

PROBLEMS = [["ACP 1", air_cargo_p1],
            ["ACP 2", air_cargo_p2],
            ["ACP 3", air_cargo_p3]]
SEARCHES = [["breadth_first_search", breadth_first_search, ""],
            ['breadth_first_tree_search', breadth_first_tree_search, ""],
            ['depth_first_graph_search', depth_first_graph_search, ""],
            ['depth_limited_search', depth_limited_search, ""],
            ['uniform_cost_search', uniform_cost_search, ""],
            ['recursive_best_first_search', recursive_best_first_search, 'h_1'],
            ['greedy_best_first_graph_search', greedy_best_first_graph_search, 'h_1'],
            ['astar_search', astar_search, 'h_1'],
            ['astar_search', astar_search, 'h_ignore_preconditions'],
            ['astar_search', astar_search, 'h_pg_levelsum'],
            ]


class PrintableProblem(InstrumentedProblem):
    """ InstrumentedProblem keeps track of stats during search, and this
    class modifies the print output of those statistics for air cargo
    problems.
    """

    def __repr__(self):
        return '{:^10d}  {:^10d}  {:^10d}'.format(self.succs, self.goal_tests, self.states)


def run_search(problem, search_function, parameter=None):

    start = timer()
    ip = PrintableProblem(problem)
    if parameter is not None:
        node = search_function(ip, parameter)
    else:
        node = search_function(ip)
    elapsed_time = timer() - start
    print("\nExpansions   Goal Tests   New Nodes")
    print("{}\n".format(ip))
    show_solution(node, elapsed_time, problem)
    print()
    return ip, elapsed_time, node

def manual():

    print(PROBLEM_CHOICE_MSG)
    for idx, (name, _) in enumerate(PROBLEMS):
        print("    {!s}. {}".format(idx+1, name))
    p_choices = input("> ").split()

    print(SEARCH_METHOD_CHOICE_MSG)
    for idx, (name, _, heuristic) in enumerate(SEARCHES):
        print("    {!s}. {} {}".format(idx+1, name, heuristic))
    s_choices = input("> ").split()

    main(p_choices, s_choices)

    print("\nYou can run this selection again automatically from the command " +
          "line\nwith the following command:")
    print("\n  python {} -p {} -s {}\n".format(__file__,
                                               " ".join(p_choices),
                                               " ".join(s_choices)))


def main(p_choices, s_choices):

    problems = [PROBLEMS[i-1] for i in map(int, p_choices)]
    searches = [SEARCHES[i-1] for i in map(int, s_choices)]

    results = []

    for pname, p in problems:

        for sname, s, h in searches:
            hstring = h if not h else " with {}".format(h)
            print("\nSolving {} using {}{}...".format(pname, sname, hstring))

            _p = p()
            _h = None if not h else getattr(_p, h)
            pp, elapsed_time, node = run_search(_p, s, _h)
            results.append([pname, sname+" "+h, elapsed_time, 
                            len(node.solution()), pp.succs, 
                            pp.goal_tests, pp.states])


    import pandas as pd
    res = pd.DataFrame(results, columns=['Problem', 'Search', 'Elapsed Time', 
                                         'Solution size', 'Node Expansions',
                                         'Goal Tests', 'New Nodes'])
    
    fileName = "results_p("+str(p_choices)+")s("+str(s_choices)+")"

    print(res.to_csv(sep='|', index=False, float_format='%.2f')) 
    writer = pd.ExcelWriter(fileName+'.xlsx')
    res.to_excel(writer, 'Results')
    writer.save()
    #print(res.to_html())

    visualize(res, fileName)

def visualize(result, fileName):
    from altair import Chart, Color, Y, Scale


    #chart = LayeredChart(result)
    #chart += Chart().mark_line().encode(x='Search:O', y='Elapsed Time:Q')
    

    chart = Chart(result).mark_point().encode(
        #x='Search:O', color='Problem:O', y=Y('Elapsed Time:Q',
        #scale=Scale(type='log')))
        x='Search:O', color='Problem:O', y='Elapsed Time:Q')
#    with open('out.html', 'w') as f:
#       f.write(html) 
    chart.savechart(fileName+".svg")

def show_solution(node, elapsed_time, problem):
    print("Plan length: {}  Time elapsed in seconds: {}".format(len(node.solution()), elapsed_time))
    for action in node.solution():
        print("{}{}".format(action.name, action.args))

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Solve air cargo planning problems " + 
        "using a variety of state space search methods including uninformed, greedy, " +
        "and informed heuristic search.")
    parser.add_argument('-m', '--manual', action="store_true",
                        help="Interactively select the problems and searches to run.")
    parser.add_argument('-p', '--problems', nargs="+", choices=range(1, len(PROBLEMS)+1), type=int, metavar='',
                        help="Specify the indices of the problems to solve as a list of space separated values. Choose from: {!s}".format(list(range(1, len(PROBLEMS)+1))))
    parser.add_argument('-s', '--searches', nargs="+", choices=range(1, len(SEARCHES)+1), type=int, metavar='',
                        help="Specify the indices of the search algorithms to use as a list of space separated values. Choose from: {!s}".format(list(range(1, len(SEARCHES)+1))))
    args = parser.parse_args()

    if args.manual:
        manual()
    elif args.problems and args.searches:
        main(list(sorted(set(args.problems))), list(sorted(set((args.searches)))))
    else:
        print()
        parser.print_help()
        print(INVALID_ARG_MSG)
        print("Problems\n-----------------")
        for idx, (name, _) in enumerate(PROBLEMS):
            print("    {!s}. {}".format(idx+1, name))
        print()
        print("Search Algorithms\n-----------------")
        for idx, (name, _, heuristic) in enumerate(SEARCHES):
            print("    {!s}. {} {}".format(idx+1, name, heuristic))
        print()
        print("Use manual mode for interactive selection:\n\n\tpython run_search.py -m\n")
