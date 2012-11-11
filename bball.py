###
# Colin Poindexter
# bball.py
# Function utilizing a graph to select the basketball players which have proven to play best with one another.
#
# REQUIRES: 
#   - networkx (Available here: http://networkx.lanl.gov/download.html)
#   - csv
#   - math
#   - Players Lists (included)
#
# Takes player data from http://www.basketball-reference.com
#
# Copyright 2012 Colin Poindexter

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

import networkx as nx
import csv
import pprint
import math
years=[]
years.extend(str(x+1) for x in range(1940,2013))
teams = ['76ers', 'Nets', 'Celtics', 'Lakers']
players = {}

DG=nx.DiGraph()

for y in years:
    yearTeams = {}
    for t in teams:
        yearTeams[t+'-'+y] = []
    players[y] = yearTeams


def calculatePlayerScore(FG = 0, FGA = 0, TP=0, TPA=0, FT=0, FTA=0, G=1, PF=1, AST=1, MP = 0, PTS = 0):
    """Caluates a player score for any given player. Takes FG (Field Goal;s), FGA (Field Goals Attempted), TP (Three-point shots), TPA (Three-point shots Attempted), FT (Free-throws), FTA (Free-throws Attempted), G (Games), PF (Personal Fouls), MP (Minutes played), PTS (Points per game). Returns a score.""" 
    if FG == '':
        FG = 0
    if TP == '':
        TP = 0
    if FT == '':
        FT = 0
    if FGA == '':
        FGA = 0
    if TPA == '':
        TPA = 0
    if FTA == '':
        TPA = 0
    if MP == '':
        MP = 0
    if PTS=='':
        PTS = 0
    win = (int(FG) + int(TP) + int(FT))/int(G)
    tries = (int(FGA) + int(TPA) + int(FTA))/int(G)
    try:
        prePenaltyTotal = win/tries
    except:
        prePenaltyTotal = 0

    total = (prePenaltyTotal + ((int(MP)/int(G)) +.7) + (float(AST)*.9) + (float(PTS)*1.2))- (int(PF)/int(G)) 
    return total

with open('statsfile.csv', 'rb') as f:
    reader = csv.reader(f)
    rowIter = 0
    for row in reader:
        if(rowIter!=0):
            playerYears = []
            playerYears.extend(str(x+1) for x in range(int(row[2]),int(row[3])))
            team = row[-1]
            playerScore = calculatePlayerScore(row[7], row[8], row[9], row[10], row[11], row[12], row[5], row[19], row[27], row[6], row[25])
            for py in playerYears:
                players[py][team+'-'+py].append({'name': row[1], 'playerScore': playerScore})
        rowIter +=1

edges = []
for year in players.iteritems():
    for team in year[1].iteritems():
        for player in team[1]:
            name = player['name']
            score = player['playerScore']
            for teamPlayers in team[1]:
                if((name,teamPlayers['name'])) in edges:
                    DG.add_weighted_edges_from([(name,teamPlayers['name'], (score+teamPlayers['playerScore'])*2)])
                else:
                    DG.add_weighted_edges_from([(name,teamPlayers['name'], (score+teamPlayers['playerScore']))])
                    edges.append((name,teamPlayers['name']))
            


def cliques_containing_node(G,nodes=None,cliques=None):
    """Returns a list of cliques containing the given node.

    Returns a single list or list of lists depending on input nodes.
    Optional list of cliques can be input if already computed.
    """
    proximityDict  = {}
    finalList = []
    if cliques is None:
        cliques=list(find_cliques(G))

    if nodes is None:
        nodes=G.nodes()   # none, get entire graph
    if not isinstance(nodes, list):   # check for a list
        v=nodes
        # assume it is a single value
        vcliques=[c for c in cliques if v in c]
    else:
        vcliques={}
        for v in nodes:
            vcliques[v]=[c for c in cliques if v in c]
    for playerList in vcliques:
        proximityValue = 0
        for currentPlayer in playerList:
            proximityValue += G[nodes][currentPlayer]['weight']

        proximityDict[proximityValue] = playerList
    keylist = proximityDict.keys()
    keylist.sort()
    for key in keylist:
        finalList.append(proximityDict[key])
    return finalList


def strongly_connected_components(G):
    """Return nodes in strongly connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
       An directed graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.
       The list is ordered from largest connected component to smallest.

    See Also
    --------
    connected_components

    Notes
    -----
    Uses Tarjan's algorithm with Nuutila's modifications.
    Nonrecursive version of algorithm.

    References
    ----------
    .. [1] Depth-first search and linear graph algorithms, R. Tarjan
       SIAM Journal of Computing 1(2):146-160, (1972).

    .. [2] On finding the strongly connected components in a directed graph.
       E. Nuutila and E. Soisalon-Soinen
       Information Processing Letters 49(1): 9-14, (1994)..
    """
    preorder={}
    lowlink={}
    scc_found={}
    scc_queue = []
    scc_list=[]
    i=0     # Preorder counter
    for source in G:
        if source not in scc_found:
            queue=[source]
            while queue:
                v=queue[-1]
                if v not in preorder:
                    i=i+1
                    preorder[v]=i
                done=1
                v_nbrs=G[v]
                for w in v_nbrs:
                    if w not in preorder:
                        queue.append(w)
                        done=0
                        break
                if done==1:
                    lowlink[v]=preorder[v]
                    for w in v_nbrs:
                        if w not in scc_found:
                            if preorder[w]>preorder[v]:
                                lowlink[v]=min([lowlink[v],lowlink[w]])
                            else:
                                lowlink[v]=min([lowlink[v],preorder[w]])
                    queue.pop()
                    if lowlink[v]==preorder[v]:
                        scc_found[v]=True
                        scc=[v]
                        while scc_queue and preorder[scc_queue[-1]]>preorder[v]:
                            k=scc_queue.pop()
                            scc_found[k]=True
                            scc.append(k)
                        scc_list.append(scc)
                    else:
                        scc_queue.append(v)
    scc_list.sort(key=len,reverse=True)
    return scc_list
def find_cliques(G):
    """Search for all maximal cliques in a graph.

    Maximal cliques are the largest complete subgraph containing
    a given node.  The largest maximal clique is sometimes called
    the maximum clique.

    Returns
    -------
    generator of lists: genetor of member list for each maximal clique

    See Also
    --------
    find_cliques_recursive :
    A recursive version of the same algorithm

    Notes
    -----
    To obtain a list of cliques, use list(find_cliques(G)).

    Based on the algorithm published by Bron & Kerbosch (1973) [1]_
    as adapated by Tomita, Tanaka and Takahashi (2006) [2]_
    and discussed in Cazals and Karande (2008) [3]_.
    The method essentially unrolls the recursion used in
    the references to avoid issues of recursion stack depth.

    This algorithm is not suitable for directed graphs.

    This algorithm ignores self-loops and parallel edges as
    clique is not conventionally defined with such edges.

    There are often many cliques in graphs.  This algorithm can
    run out of memory for large graphs.

    References
    ----------
    .. [1] Bron, C. and Kerbosch, J. 1973.
       Algorithm 457: finding all cliques of an undirected graph.
       Commun. ACM 16, 9 (Sep. 1973), 575-577.
       http://portal.acm.org/citation.cfm?doid=362342.362367

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi,
       The worst-case time complexity for generating all maximal
       cliques and computational experiments,
       Theoretical Computer Science, Volume 363, Issue 1,
       Computing and Combinatorics,
       10th Annual International Conference on
       Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28-42
       http://dx.doi.org/10.1016/j.tcs.2006.06.015

    .. [3] F. Cazals, C. Karande,
       A note on the problem of reporting maximal cliques,
       Theoretical Computer Science,
       Volume 407, Issues 1-3, 6 November 2008, Pages 564-568,
       http://dx.doi.org/10.1016/j.tcs.2008.05.010
    """
    # Cache nbrs and find first pivot (highest degree)
    maxconn=-1
    nnbrs={}
    pivotnbrs=set() # handle empty graph
    for n,nbrs in G.adjacency_iter():
        nbrs=set(nbrs)
        nbrs.discard(n)
        conn = len(nbrs)
        if conn > maxconn:
            nnbrs[n] = pivotnbrs = nbrs
            maxconn = conn
        else:
            nnbrs[n] = nbrs
    # Initial setup
    cand=set(nnbrs)
    smallcand = set(cand - pivotnbrs)
    done=set()
    stack=[]
    clique_so_far=[]
    playerMassScore = 0
    # Start main loop
    while smallcand or stack:
        try:
            # Any nodes left to check?
            n=smallcand.pop()
        except KeyError:
            # back out clique_so_far
            cand,done,smallcand = stack.pop()
            clique_so_far.pop()
            continue
        # Add next node to clique
        clique_so_far.append(n)
        cand.remove(n)
        done.add(n)
        nn=nnbrs[n]
        new_cand = cand & nn
        new_done = done & nn
        # check if we have more to search
        if not new_cand:
            if not new_done:
                # Found a clique!
                yield clique_so_far[:]
            clique_so_far.pop()
            continue
        # Shortcut--only one node left!
        if not new_done and len(new_cand)==1:
            yield clique_so_far + list(new_cand)
            clique_so_far.pop()
            continue
        # find pivot node (max connected in cand)
        # look in done nodes first
        numb_cand=len(new_cand)
        maxconndone=-1
        for n in new_done:
            cn = new_cand & nnbrs[n]
            conn=len(cn)
            if conn > maxconndone:
                pivotdonenbrs=cn
                maxconndone=conn
                if maxconndone==numb_cand:
                    break
        # Shortcut--this part of tree already searched
        if maxconndone == numb_cand:
            clique_so_far.pop()
            continue
        # still finding pivot node
        # look in cand nodes second
        maxconn=-1
        for n in new_cand:
            cn = new_cand & nnbrs[n]
            conn=len(cn)
            if conn > maxconn:
                pivotnbrs=cn
                maxconn=conn
                if maxconn == numb_cand-1:
                    break
        # pivot node is max connected in cand from done or cand
        if maxconndone > maxconn:
            pivotnbrs = pivotdonenbrs
        # save search status for later backout
        stack.append( (cand, done, smallcand) )
        cand=new_cand
        done=new_done
        smallcand = cand - pivotnbrs

G = DG.to_undirected(True)

def main():
    playersList = []
    playersPlayed = []
    print('===== TYPE "Done" WHEN DONE ======')
    player = str(raw_input('What player do you want to start with? '))
    playersList.append(player)
    j = 0
    c = cliques_containing_node(G, player)
    while player!='Done':
        if(len(c)>0):
            playersPlayed.append((c[0]))

            if(j==0):
                print('Players '+player+' plays well with')
            else:
                print('Players '+currentSelected+' plays well with')
            j+=1
            i = 0
            for player in c[0]:
                print(str(i)+"   "+player)
                i +=1
            player = str(raw_input('Which player above do you want to continue your team with? '))
            if(c[0][int(player)] in playersList):
                print('Oops!, you already selected '+c[0][int(player)]+' please choose again.')
                player = str(raw_input('Which player above do you want to continue your team with? '))
                i = 0
                for player in c[0]:
                    print(str(i)+"   "+player)
                    i +=1
            if(player=='Done'):
                break

            playersList.append(c[0][int(player)])
            currentSelected = c[0][int(player)]
            c = cliques_containing_node(G, c[0][int(player)])
            if(len(c)>0):
                for triedList in playersPlayed:
                    try:
                        if((c[0]) in playersPlayed):
                            c.remove(c[0])
                    except:
                        break
        else:
            print('SORRY! No more players available.')
            break

    print("Here's your team!")
    for finalPlayer in playersList:
        print(finalPlayer)

    return
main()




