#balls

# # # # #
# importing the relevant libraries
import random
import constants
import GazeContingency as GC
import math
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import libinput
from pygaze import eyetracker

# # # # # # 
#experiment setup

# start timing
libtime.expstart()

# create display object
disp = libscreen.Display()

# create eyetracker object
tracker = eyetracker.EyeTracker(disp)

# create keyboard object
keyboard = libinput.Keyboard(keylist=['space', 'escape', 'r'], timeout=None)

# create logfile object
log = liblog.Logfile()
log.write(["trialnr", "targetNr"])

# create trial and block variables
trialNo = 0
blockNo = -1
targetNo = -1
trialIndex = 0


# # # # # 1
#some functions

def DrawCircle(screen):
    pointList = []
    for i in range(constants.CIRCLEPOLYGONCOUNT):

        rad = i/constants.CIRCLEPOLYGONCOUNT*math.tau
        print(rad, end=" ")
        x,y = (math.cos(rad)*constants.TARGETAREARADIUS+constants.SCREENMIDPOINT[0], math.sin(rad)*constants.TARGETAREARADIUS+constants.SCREENMIDPOINT[1])
        print(x,y)
        pointList.append([x,y])

    if isinstance(screen, GC.Screen):
        screen.screen.draw_polygon(pointList, colour=constants.CIRCLECOLOUR, fill=True)
    elif isinstance(screen, libscreen.Display):
        screen.draw_polygon(pointList, colour=constants.CIRCLECOLOUR, fill=True)

def GetTargetCoordinates(targetNumber):
    global targetNo
    print(f"getting coordinates for target no {targetNumber}. ", end="")
    rad = targetNumber/targetCount*math.tau
    x,y = (math.cos(rad)*constants.TARGETDISTANCE, math.sin(rad)*constants.TARGETDISTANCE)
    print(f"Found: ({constants.SCREENMIDPOINT[0]+x},{ constants.SCREENMIDPOINT[1]+y})")

    print(f"Possible confound with target No {targetNo}")
    return(constants.SCREENMIDPOINT[0]+x, constants.SCREENMIDPOINT[1]+y)

sqrt2half = math.sqrt(2) #we'll need this later

def GetRoughArea(pos, distAllowed, inscribed = False): #returns (xmin, xmax, ymin, ymax)
    
    if inscribed:
        radius = distAllowed * sqrt2half
    else:
        radius = distAllowed

    print("")

    x = pos[0]
    y = pos[1]
    
    xmin, xmax = x-radius, x+radius
    ymin, ymax = y-radius, y+radius

    return (xmin, xmax, ymin, ymax)

def Distance(pos1, pos2):
    return(math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2))

def CheckGazeOnInscribed(pos, gazePos, distAllowed):

    xmin, xmax, ymin, ymax = GetRoughArea(pos, distAllowed, True)

    if(gazePos[0] > xmax or gazePos[0] < xmin or gazePos[1] < ymin or gazePos[1] > ymax):
        #gaze might be OFF target
        #calculate distance
        d = Distance(gazePos, pos)
        if d > distAllowed:
            return False
    return True

def CheckGazeOnExcribed(pos, gazePos, distAllowed):
    xmin, xmax, ymin, ymax = GetRoughArea(pos, distAllowed, False)

    if(gazePos[0] < xmin or gazePos[0] > xmax or gazePos[1] < ymin or gazePos[1] > ymax):
        #gaze definitely OFF target
        return False
    else:
        d = Distance(gazePos, pos)
        if d > distAllowed:
            return False
    return True


def FixationTime():
    return constants.FIXATIONTIME
def TarFixationTime():
    return constants.TARTIME



#Create GazeContingency Object
GCTrials = GC.GazeContingency(disp, tracker,keyboard, constants.SCREENREFRESHRATE)
#create rules that count on every Screen




#populate GC objects

#Screens and #Rules
inscreen = libscreen.Screen()
inscreen.draw_text(text="When you see a circle, look at it. When the circle disappears, look back to the fixation cross.\n\n(press space to start)", fontsize=24)


#interTextRecalibrate
GCTrials.AddScreen("(Re)calibration will now occur", 'interTextRecalibrate')


#---------------------------------------------
#fixGazeOff
fixGazeOffScreen = GC.Screen(GCTrials)
fixGazeOffScreen.screen.draw_circle(pos=constants.SCREENMIDPOINT, r=constants.TARGETAREARADIUS, fill=True, colour = constants.CIRCLECOLOUR)
DrawCircle(fixGazeOffScreen)
fixGazeOffScreen.screen.draw_circle(pos=constants.SCREENMIDPOINT, r=constants.TARGETSIZE, fill=True, colour = 'black')
GCTrials.AddScreen(fixGazeOffScreen, 'fixGazeOff')
#rules
#from fixGazeOff to fixGazeOn when Gaze is ON fixation
fixGazeOffRule1 = GC.Rule(constants.INTERTIME_CHECKGAZEPOS, lambda: CheckGazeOnExcribed(constants.SCREENMIDPOINT ,tracker.sample(),constants.GAZEREGION))
GCTrials.AddRule('fixGazeOn', fixGazeOffRule1, 'fixGazeOff')

#---------------------------------------------
#fixGazeOn
fixGazeOnScreen = GC.Screen(GCTrials)
fixGazeOnScreen.screen.draw_circle(pos=constants.SCREENMIDPOINT, r=constants.TARGETAREARADIUS, fill=True, colour = constants.CIRCLECOLOUR)
DrawCircle(fixGazeOnScreen)
fixGazeOnScreen.screen.draw_circle(pos=constants.SCREENMIDPOINT, r=constants.TARGETSIZE, fill=True, colour = 'black')
GCTrials.AddScreen(fixGazeOnScreen, 'fixGazeOn')
#rules
#from fixGazeOn to fixGazeOff when Gaze is OFF fixation
fixGazeOnRule1 = GC.Rule(constants.INTERTIME_CHECKGAZEPOS, lambda: not CheckGazeOnInscribed(constants.SCREENMIDPOINT, tracker.sample(), constants.GAZEREGION))
GCTrials.AddRule('fixGazeOff', fixGazeOnRule1, 'fixGazeOn')



#todo: write function/method that updates the tarNo variable and updates screens
def UpdateTarget(shuffle = True):

    global targetNo
    #refresh target
    if shuffle:
        targetNo = random.choice(range(targetCount))


    GCTrials.AddScreen(targetscreens[targetNo], 'tarGazeOn')
    GCTrials.AddScreen(targetScreensGazeOff[targetNo], 'tarGazeOff')
    #log target no and coordinates
    tracker.log(f'T: target: {targetNo}')

#create GCScreens for GazeContingency objects

targetscreens = {}
targetScreensGazeOff = {}
targetPoss = {}
targetCount = 8



#A really weird bug occurs here. The last target screens to be initialised would always be drawn like the 0th target screens to be initialised
#I was unable to fix this bug, so that is why 1 extra target screen is drawn in this loop
#the last target screen to be drawn here will never be shown, that is determined in the UpdateTarget() method
for i in range(targetCount+1):
    targetNo = i
    targetscreens[i] = GC.Screen(GCTrials)
    DrawCircle(targetscreens[i])
    targetscreens[i].screen.draw_circle(pos=GetTargetCoordinates(i), r=constants.TARGETSIZE, fill=True, colour = 'black')
    targetScreensGazeOff[i] = GC.Screen(GCTrials)
    DrawCircle(targetScreensGazeOff[i])
    targetScreensGazeOff[i].screen.draw_circle(pos=GetTargetCoordinates(i), r=constants.TARGETSIZE, fill=True, colour = 'black')
    targetPoss[i] = GetTargetCoordinates(i)


def targetPosDict(i):
    return targetPoss[i]

#this function is basically the trialhandler
#it is called whenever fixation time on the fixation is reached
#from fixGazeOn to custom behaviour when time is reached 
#
#               to interTextBlockOver       when also trial == constants.TRIALS
#               to interTextPracticeOver    when also block==0, 
#               to textExperimentOver       when also block == constants.BLOCKS-1
#               to tarGazeOff               when also nothing

def fixGazeOnRule2CustomBehaviour():
    global blockNo, trialNo, targetNo, trialIndex
    UpdateTarget()
    
    #if block < 0 (practice) and practice trials are completed
    if blockNo < 0 and trialNo == constants.TRIALSPRAC:
        blockNo += 1
        trialNo = 0
        trialIndex += 1
        GCTrials.GotoScreen('interTextPracticeOver')
    #case: not practice, and trials of one block are completed
    elif blockNo >= 0 and trialNo == constants.TRIALS:
        #if blockNo is equal to total blocks
        if blockNo == constants.BLOCKS:
            GCTrials.GotoScreen('experiment over', True)
            # end the experiment
            log.close()
            tracker.close()
            disp.close()
            libtime.expend()
        #case: not practice, not all blocks completed, but one block completed
        else:
            blockNo += 1
            trialNo = 0
            trialIndex += 1
            GCTrials.GotoScreen('interTextBlockOver')

    #case: not trialNo == trialsTotal
    else:
        trialNo += 1
        trialIndex += 1
        GCTrials.GotoScreen('tarGazeOff')

    #log trial and block
    tracker.log(f'T: trialIndex {trialIndex} @startTrial {trialNo} @block {blockNo} @tar {targetNo}')


    
fixGazeOnRule2 = GC.Rule(1, lambda: GCTrials.timeOnScreen >= FixationTime())
GCTrials.AddRule(fixGazeOnRule2CustomBehaviour, fixGazeOnRule2,'fixGazeOn')

#---------------------------------------------
#tarGazeOff
GCTrials.AddScreen(targetScreensGazeOff[targetNo], 'tarGazeOff')
#rules
#from tarGazeOff to tarGazeOn when Gaze is ON target
tarGazeOffRule1 = GC.Rule(constants.INTERTIME_CHECKGAZEPOS, lambda: CheckGazeOnExcribed(targetPosDict(targetNo), tracker.sample(), constants.GAZEREGION))
GCTrials.AddRule('tarGazeOn', tarGazeOffRule1, 'tarGazeOff')
#---------------------------------------------
#tarGazeOn
GCTrials.AddScreen(targetscreens[targetNo], 'tarGazeOn')
#rules
#from tarGazeOn to tarGazeOff when Gaze is OFF target
tarGazeOnRule1 = GC.Rule(constants.INTERTIME_CHECKGAZEPOS, lambda: not CheckGazeOnInscribed(targetPosDict(targetNo), tracker.sample(), constants.GAZEREGION))
GCTrials.AddRule('tarGazeOff', tarGazeOnRule1, 'tarGazeOn')
#from tarGazeOn to fixGazeOff when Gaze is ON target for TARTIME()
tarGazeOnRule2 = GC.Rule(1, lambda: GCTrials.timeOnScreen >= TarFixationTime())
GCTrials.AddRule('fixGazeOff', tarGazeOnRule2, 'tarGazeOn')

#---------------------------------------------
#interTextPracticeOver
GCTrials.AddScreen("Practice is now over. The real experiment will begin", 'interTextPracticeOver')
#rules 
#from interTextPracticeOver to fixGazeOff when button pressed
interTextPracticeOverRule1 = GC.Rule(1, lambda: keyboard.get_key('space')[0]=='space')
GCTrials.AddRule('fixGazeOff', interTextPracticeOverRule1,'interTextPracticeOver')


#---------------------------------------------
#interTextBlockOver
GCTrials.AddScreen("You have completed a block. You may take a short break. The researcher can start recalibration now", 'interTextBlockOver')
#rules


#from interTextBlockOver to fixGazeOff when space is pressed
interTextBlockOverRule2 = GC.Rule(50, lambda: GCTrials.GetIfKey('space', reset="all"))
GCTrials.AddRule('fixGazeOff', interTextBlockOverRule2, 'interTextBlockOver')

#########
# add rules for every frame 

# to interTextBlockOver or to recalibration when 'r' is pressed
#alwaysrule1 function definition
def alwaysRule1Lambda():
    return GCTrials.GetIfKey('r', reset="all")

alwaysRule1 = GC.Rule(50, alwaysRule1Lambda)


def void_alwaysRule1Command_Result1():
    tracker.log('Starting recalibration')
    tracker.stop_recording()
    tracker.calibrate()
    tracker.start_recording()



def void_alwaysRule1Command_Result2():
    #return to interTextBlockOver 
    GCTrials.GotoScreen('interTextBlockOver')
    #do something to trials, and shuffle target
    global trialNo, trialIndex, blockNo, targetNo
    subtract = 10

      
    startSubtract = trialNo
    if trialNo > subtract:
        trialNo -= subtract
    else: 
        trialNo = 0

    UpdateTarget()

    #log the reset
    tracker.log(f'D: subtracted {startSubtract-trialNo} from {startSubtract}')
    tracker.log(f'T: trialIndex {trialIndex} @startTrial {trialNo} @block {blockNo} @tar {targetNo}')

def alwaysRule1Command():
    #choose between going back to interTextBlockOver, or to start recalibration
    # if on screen interTextBlockOver, do #2
    key = str(GCTrials.screenCurrent)

    print(f'keypress R detected @ screen {key} doing the following:')

    if key=='interTextBlockOver':
        return void_alwaysRule1Command_Result1()
    elif key in ['tarGazeOff', 'tarGazeOn', 'fixGazeOn', 'fixGazeOff']:
        return void_alwaysRule1Command_Result2()
    
                     
GCTrials.AddRule(alwaysRule1Command, alwaysRule1)



# # # # #
# run the experiment

# calibrate eye tracker
tracker.calibrate()

# show instructions
disp.fill(inscreen)
disp.show()
keyboard.get_key()

tracker.start_recording()



print('only one line to go!')
#run blocks
GCTrials.Loop(libtime, 'fixGazeOff')



