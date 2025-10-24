
import networkx as nx


def algo3(json_data):
    g = nx.DiGraph()
     
    last_decision_task = []  
    
    for i in range(len(json_data["steps"])):
        
        
        if 'Task' in json_data["steps"][i]:
            current_element = str(json_data["steps"][i]['Task']['Actor'] + ":" + json_data["steps"][i]['Task']['Action'])
            
            if not json_data["steps"][i]['Task']['Gateway Path']:
                
                if i == 0:
                    
                    
                    g.add_node(current_element) 
                   
                    last_element = current_element
                else:
                    
                    g.add_edge(last_element, current_element)
                    last_element = current_element
            else:
                
                last_element_path= None
                while last_element_path == None:
                    for c in range(len(last_decision_task)):

                        all_paths = traverse_paths3(g, last_decision_task[0-c])
                        for path in all_paths:
                            if "Task" in json_data["steps"][i]:
                                if json_data["steps"][i]['Task']['Gateway Path'] in path:
                                    last_element_path = path[-1]
                                    break 
                            
                            else:
                                for pa in path:
                                    if "Task" in json_data["steps"][i]:
                                        if json_data["steps"][i]['Task']['Gateway Path'] in pa:
                                            last_element_path = path[-1]
                                            break
                                        
                
                g.add_edge(last_element_path, current_element)
                last_element = current_element
                
        if 'Event' in json_data["steps"][i]:
            
            current_element = str("(" +json_data["steps"][i]['Event']['Type']+" " + json_data["steps"][i]['Event']['Name'] + ")")
            if not json_data["steps"][i]['Event']['Gateway Path']:
                if i == 0:
                    
                    for j in range(1,len(json_data["steps"])):
                         if  'Task' in json_data["steps"][j]:
                             current_element= str(json_data["steps"][j]['Task']['Actor']+ ":")+ current_element
                             break
                         
                    g.add_node(current_element)   
                    last_element = current_element
                else:
                    g.add_edge(last_element,current_element)
                    last_element = current_element
            else:
               
                last_element_path= None
                while last_element_path == None:
                    
                    for c in range(len(last_decision_task)):
                        all_paths = traverse_paths3(g, last_decision_task[0-c])
                        for path in all_paths:
                            if json_data["steps"][i]['Event']['Gateway Path'] in path:
                                last_element_path = path[-1]
                                break
                            
                            else:
                                for pa in path:
                                    
                                    if json_data["steps"][i]['Event']['Gateway Path'] in pa:
                                        last_element_path = path[-1]
                                        break
                
                g.add_edge(last_element_path, current_element)
                last_element = current_element
        if 'Gateway' in json_data["steps"][i]:
            
            
            if json_data["steps"][i]['Gateway']['type'] == "Exclusive Gateways":
                
                if not json_data["steps"][i]['Gateway']['Previous Gateway Path']: 

                    last_decision_task.append(str(json_data["steps"][i]['Gateway']['decision task']))
                    g.add_edge(last_element, last_decision_task[-1])
                    last_element = last_decision_task[-1]
                    
                    # Ajouter les branches de la passerelle
                    for p in json_data["steps"][i]['Gateway']['Path']:
                        
                        g.add_edge(last_element, p)
                    last_element = p
                else:
                    
                    last_element_path= None
                    while last_element_path == None:
                        
                        for c in range(len(last_decision_task)):
                            all_paths = traverse_paths3(g, last_decision_task[0-c])
                            for path in all_paths:
                                
                                if json_data["steps"][i]['Gateway']['Previous Gateway Path'] in path:
                                    last_element_path = path[-1]
                                    break
                                    
                                    
                                else:
                                    for pa in path:
                                        if json_data["steps"][i]['Gateway']['Previous Gateway Path'] in pa:
                                            last_element_path = path[-1]
                                            break
                    last_decision_task.append(json_data["steps"][i]['Gateway']['decision task'])
                    
                    g.add_edge(last_element_path, last_decision_task[-1])
                    last_element=last_decision_task[-1]
                    for p in json_data["steps"][i]['Gateway']['Path']:
                        if p in list(g.nodes()):
                            p+=' '
                        g.add_edge(last_element, p)
                    
                    last_element = p  

            elif json_data["steps"][i]['Gateway']['type'] == "Event Gateways":
                 if not json_data["steps"][i]['Gateway']['Previous Gateway Path']:

                   for p in json_data["steps"][i]['Gateway']['Event Branches']:
                      #print(p)
                      event="("+ p["Event Type"]+ p["Event Name"]+")"
                      g.add_edge(last_element,event)
                      last_element = event
                   last_decision_task.append(last_element)   
                 else:
                    
                    all_paths = traverse_paths3(g, last_decision_task[-1])
                    for path in all_paths:
                      if json_data["steps"][i]['Gateway']['Previous Gateway Path'] in path:
                        last_element = path[-1]
                        break
                    for p in json_data["steps"][i]['Gateway']['Event Branches']:
                      
                      event="("+ p["Event Type"]+ p["Event Name"]+")"
                      g.add_edge(last_element,event)
                      last_element = event
        
                    last_decision_task.append(last_element)
    
    start_node = list(g.nodes())[0]
    
    all_pathes = traverse_paths3(g, start_node)
    
    sketches=""
    for path in all_pathes:
        sketches+=('\n')
        for p in path:
            sketches+=(p)
            sketches+=" "
            sketches+="\n"
    
    lines = sketches.splitlines()

    if ":" not in lines[0]:
        sketches = lines[1].split(":")[0] + ":" + sketches
    return sketches  

def is_terminal_node(graph, node):
    return len(graph.get(node, [])) == 0

def traverse_paths3(graph, current_node, visited=None, path=None):
    # Initialisation des paramètres
    if visited is None:
        visited = set()  
    if path is None:
        path = []  

    
    visited.add(current_node)
    path.append(current_node)


    if not list(graph.successors(current_node)):  
        return [list(path)]

    all_paths = []
    for neighbor in graph.successors(current_node):
        if neighbor not in visited:  
            all_paths.extend(traverse_paths3(graph, neighbor, visited.copy(), path.copy()))

    return all_paths
