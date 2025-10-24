import networkx as nx

def traverse_paths2(graph, start_node):
    all_paths = []
    stack = [(start_node, [start_node])] 
    visited_global = set() 

    while stack:
        node, path = stack.pop()
        path_tuple = tuple(path)  # Convert list to tuple for hashability
        if path_tuple in visited_global:
            raise ValueError(f"Infinite loop detected: revisiting path {path}")
        visited_global.add(path_tuple)

        # If it's a terminal node, add the complete path
        if len(list(graph.successors(node))) == 0:
            all_paths.append(path)
        else:
            for neighbor in graph.successors(node):
                if neighbor not in path:  # Avoid revisiting nodes in the current path
                    stack.append((neighbor, path + [neighbor]))
    return all_paths

def resolve_last_element_path(graph, last_decision_tasks, gateway_path):
    """
    Resolve the last element in the path corresponding to the given gateway path.
    """
    for task in reversed(last_decision_tasks):  # Start with the most recent task
        all_paths = traverse_paths2(graph, task)
        for path in all_paths:
            if gateway_path in path:
                return path[-1]  # Return the last element in the matching path
    return None  # If no match is found

def algo2(json_data):
    g = nx.DiGraph()
    last_decision_task = []  # Store the last decision task for gateways
    i = 0
    for step in json_data["steps"]:

        if 'Task' in step:
            current_element = f"{step['Task']['Actor']}: {step['Task']['Action']}"
            if not step['Task']['Gateway Path']:
                if g.number_of_nodes() == 0:  # First node
                    g.add_node(current_element)
                else:
                    g.add_edge(last_element, current_element)
                last_element = current_element
            else:
                last_element_path = resolve_last_element_path(g, last_decision_task, step['Task']['Gateway Path'])
                if last_element_path:
                    g.add_edge(last_element_path, current_element)
                    last_element = current_element

        elif 'Event' in step:
            current_element = f"({step['Event']['Type']} {step['Event']['Name']})"
            if not step['Event']['Gateway Path']:
                if g.number_of_nodes() == 0:  # First node
                    g.add_node(current_element)
                else:
                    g.add_edge(last_element, current_element)
                last_element = current_element
            else:
                last_element_path = resolve_last_element_path(g, last_decision_task, step['Event']['Gateway Path'])
                if last_element_path:
                    g.add_edge(last_element_path, current_element)
                    last_element = current_element

        elif 'Gateway' in step:

            if i == 0:
                # Special case for the first Gateway
                current_element = json_data["steps"][i]['Gateway']['decision task']
                g.add_node(current_element)  # Add the decision task as a standalone node
                last_decision_task.append(current_element)
                last_element = current_element  # Initialize last_element
            else:
                if step['Gateway']['type'] == "Exclusive Gateways":
                    decision_task = step['Gateway']['decision task']
                    last_decision_task.append(decision_task)
                    if not step['Gateway']['Previous Gateway Path']:
                        g.add_edge(last_element, decision_task)
                    else:
                        last_element_path = resolve_last_element_path(g, last_decision_task, step['Gateway']['Previous Gateway Path'])
                        if last_element_path:
                            g.add_edge(last_element_path, decision_task)  
                    if step['Gateway']['Path']:    #test        
                        for path in step['Gateway']['Path']:
                            g.add_edge(decision_task, path)
                elif step['Gateway']['type'] == "Event Gateways":
                    for branch in step['Gateway']['Event Branches']:
                        event = f"({branch['Event Type']} {branch['Event Name']})"
                        g.add_edge(last_element, event)
                    last_decision_task.append(last_element)
        i += 1
        if i > 50:
            print ("Infinite Loop Avoided")
            return None

    # Traverse the graph to generate all paths
    start_node = list(g.nodes())[0]

    all_paths = traverse_paths2(g, start_node)

    # Format paths in Sketch Miner syntax
    sketches = ""
    for path in all_paths:
        sketches += "\n".join(path) + "\n\n"
    
    lines = sketches.splitlines()

    if ":" not in lines[0]:
        sketches = lines[1].split(":")[0] + ":" + sketches  

    return sketches

