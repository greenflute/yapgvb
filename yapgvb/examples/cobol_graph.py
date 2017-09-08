#!/usr/bin/env python

import sys
import re
import tempfile

try:
    import yapgvb
except ImportError:
    print "You need yapgvb module to generate graph. Please install it!!"
    exit(1)

LABEL = re.compile('^.{7}([\w-]*)')
PERFORM = re.compile('.*PERFORM ([\w-]*)')
PROC = re.compile('^.{7}PROCEDURE')

def main(filename):
    try:
        file = open(filename, 'r')
    except Exception as e:
        print "Errors occurred opening input file %s" % filename 
        print e
        exit(1)
        
    graph = yapgvb.Digraph()
    
    node_from = None
    node_to = None
    
    tmp = tempfile.NamedTemporaryFile()
    
    # set file pointer on PROCEDURE DIVISION line
    for line in file:
        if PROC.match(line):
            break
    
    # now writes to temp file, deleting comments and debug statement
    for line in file:
        try:
            if line[6] in ('*', 'D'):
                continue
        except IndexError:
            continue
            
        tmp.write(line)
        
    # look for labels and build graph
    # every label is a node, every perform is an edge
    tmp.seek(0)
    for line in tmp:
        mtch = LABEL.match(line)
        if mtch and mtch.group(1):
            #if mtch.group(1)[0:1] in ("Z-"):
            #    continue
            node_from = graph.find_node(mtch.group(1))
            
        mtch = PERFORM.match(line)
        if mtch and mtch.group(1) and mtch.group(1) != "VARYING":
            #if mtch.group(1)[0:1] in ("Z-"):
            #    continue
            node_to = graph.find_node(mtch.group(1))
            graph.add_edge(node_from, node_to)
    
    print "Graph edges: ", len([n for n in graph.edges])
    print "Graph nodes: ", len([n for n in graph.nodes])
    
    graph.layout(engine='dot')
    print "rendering graph..."
    try:
        fileoname = filename + ".jpg"
        fileout = open(fileoname, 'w')
    except Exception as e:
        print "Errors occurred opening output file %s" % fileoname 
        print e
        exit(1)
    
    graph.render(outstream=fileout,format='jpg')
    print "Done!"
    tmp.close()
    file.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Too few arguments"
        print "Usage: cblgraph.py <file-input-name>"
        exit(1)
    
    main(sys.argv[1])
        
        