'''
Created on 4. 5. 2015
@author: janbednarik
'''

from Tkinter import *
from trajectory import Trajectory
from clustering import Clustering
import sys
import numpy

#define the canvas size
canvas_width = 945
canvas_height = 285

#shift the picture so it fills the canvas
scaleX = 468
scaleY = 145

MAX_CLUSTERS = 3
MAX_CLUSTERS_USER_DEFINED = False
COLORS = ["#FF0000", # red 
          "#00FF00", # lime
          "#0000FF", # blue
          "#FFFFFF", # white
          "#FFFF00", # yellow
          "#00FFFF", # aqua
          "#FF00FF", # fuchsia
          "#800000", # maroon
          "#808000", # olive
          "#008000", # green
          "#008080", # teal
          "#000080", # navy
          "#800080", # purple
          "#808080", # gray
          "#C0C0C0"] # silver 
 
COLOR_BLACK = "#000000"

# line coordinates
xold, yold = None, None

ci = 0      # cluster index (for painting)
newT = True # Flag - a new trajectory being created

# list of the clusters of trajectories
trajectories = []
clust = Clustering()



def loadPoints(w, trajectories):
    newDict = {}
    with open('/users/sunildesai/desktop/points.csv', 'r') as f:
        for line in f:
            data = line.split(',')
            runID = data[0]
            order = float (data[1])
            xValue = float (data[2])
            yValue = float (data[3])
            if not newDict.has_key(runID):
                newDict[runID] = []
            newDict[runID].append((order, xValue, yValue))

        for runID in newDict.keys():
             newDict[runID] = sorted(newDict[runID])

        for order in newDict.keys():
             newDict[order] = sorted(newDict[order])
             
    import pprint
    pprint.pprint(newDict)

    for runID, points in newDict.iteritems():
        trajectories.append(Trajectory(0))
        xold = None
        yold = None
        for order, xValue, yValue in points:
            #scale data
            xValue = xValue * 9.2 + 150
            yValue = 400 - (yValue * 10 + 200)
            trajectories[len(trajectories) - 1].addPoint((xValue, yValue))

            ## paint one point
        #     c = COLORS[ci]
            c = COLOR_BLACK
            x1, y1 = (xValue - 2), (yValue - 2)
            x2, y2 = (xValue + 2), (yValue + 2)
            w.create_oval(x1, y1, x2, y2, fill = c)

            ## paint a line
            if xold is not None and yold is not None:
                w.create_line(xold, yold, xValue, yValue, smooth=True)

            xold = xValue
            yold = yValue

            # Check if last trajectory has 0 length
        if trajectories[len(trajectories) - 1].length() == 0.0:
            trajectories.pop()
            Trajectory.decGlobID()

def individualCluster(event, n):
    print n
    global w, trajectories
    # clear canvas
    w.delete('all')
    w.create_image(scaleX, scaleY, image=bg)
    for t in trajectories:
        if (t.getClusterIdx() == n):
            t.draw(w, COLORS[n])

def individualClusterCallback(n):
    return lambda evt: individualCluster(evt, n)



# While mouse button 1 is pressed, the trajectory is being painted and new points are saved
def buttonMotion(event):
    global newT, xold, yold

    ## save point
    # a first point for a new trajectory
    if(newT):
        trajectories.append(Trajectory(ci))
        newT = False

    trajectories[len(trajectories) - 1].addPoint((event.x, event.y))

    ## paint one point
#     c = COLORS[ci]
    c = COLOR_BLACK
    x1, y1 = (event.x - 2), (event.y - 2)
    x2, y2 = (event.x + 2), (event.y + 2)
    w.create_oval(x1, y1, x2, y2, fill = c)

    ## paint a line
    if xold is not None and yold is not None:
        w.create_line(xold, yold, event.x, event.y, smooth=True)

    xold = event.x
    yold = event.y

# Switch to next cluster
def nextCluster(event):
    global ci, ti, COLORS

    # switch to next cluster
    ci = (ci + 1) % MAX_CLUSTERS
    ti = 0
    COLOR_IDX = (ci + 1) % MAX_CLUSTERS

# Switch to next trajectory
def buttonUp(event):
    global newT, xold, yold
    newT = True
    xold = None
    yold = None

    # Check if last trajectory has 0 length
    if trajectories[len(trajectories) - 1].length() == 0.0:
        trajectories.pop()
        Trajectory.decGlobID()

# debug print trajectories
def printTrajectories(event):
    for t in trajectories:
        print(t)

def clusterTrajectoriesAgglomerative(event):
    # perform clustering
    clust.clusterAgglomerartive(trajectories, MAX_CLUSTERS)
     
    # clear canvas
    w.delete('all')

    #redraw background
    w.create_image(scaleX, scaleY, image=bg)

    # draw colored trajectories
    for t in trajectories:
        t.draw(w, COLORS[t.getClusterIdx()])

def clusterTrajectoriesSpectral(event):
    # perform clustering
    if MAX_CLUSTERS_USER_DEFINED:
        clust.clusterSpectral(trajectories, MAX_CLUSTERS)
    #else:
    clust.clusterSpectral(trajectories)
     
    # clear canvas
    w.delete('all')

    #redraw background
    w.create_image(scaleX, scaleY, image=bg)

    # draw colored trajectories
    for t in trajectories:
        t.draw(w, COLORS[t.getClusterIdx()])

def reset(event):
    trajectories[:] = []
    Trajectory.resetGlobID()
    
    # clear canvas
    w.delete('all')

    #redraw background
    w.create_image(scaleX, scaleY, image=bg)

# Command line parsing
if(len(sys.argv) == 2):
    MAX_CLUSTERS = int(sys.argv[1])
    MAX_CLUSTERS_USER_DEFINED = True
    

#print("Number of clusters: %d" % MAX_CLUSTERS)

master = Tk()
master.title( "Trajectory clustering" )

w = Canvas(master, width=canvas_width, height=canvas_height)
w.pack(expand = YES, fill = BOTH)
bg = PhotoImage(file='roundabout.gif')
bg = bg.subsample(2)
w.create_image(scaleX, scaleY, image=bg)
w.focus_set()

w.bind('<B1-Motion>', buttonMotion)
w.bind('<ButtonRelease-1>', buttonUp)
w.bind('a', clusterTrajectoriesAgglomerative)
w.bind('s', clusterTrajectoriesSpectral)
w.bind('r', reset)

for i in xrange(9):
    s = str(i+1)
    w.bind(s, individualClusterCallback(i))

loadPoints(w, trajectories)

mainloop()
