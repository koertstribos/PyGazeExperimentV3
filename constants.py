## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##    PyGaze is a Python module for easily creating gaze contingent experiments
##    or other software (as well as non-gaze contingent experiments/software)
##    Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013)
import math 

# MAIN
DUMMYMODE = False # False for gaze contingent display, True for dummy mode (using mouse or joystick)
LOGFILENAME = 'default' # logfilename, without path
LOGFILE = LOGFILENAME[:] # .txt; adding path before logfilename is optional; logs responses (NOT eye movements, these are stored in an EDF file!)


# DISPLAY
# used in libscreen, for the *_display functions. The values may be adjusted,
# but not the constant's names
SCREENNR = 0 # number of the screen used for displaying experiment
DISPTYPE = 'psychopy' # either 'psychopy' or 'pygame'
DISPSIZE = (2560,1440) # canvas size
SCREENMIDPOINT = (DISPSIZE[0]/2, DISPSIZE[1]/2)
SCREENSIZE = (59.8, 33.6) # physical display size in cm
SCREENDIST = 67.5
MOUSEVISIBLE = False # mouse visibility

BGC = (0,0,0,255) # backgroundcolour
FGC = (255,255,255,255) # foregroundcolour

#CIRCLECOLOUR
CIRCLECOLOUR = (30,30,30)

SCREENREFRESHRATE = 100
SCREENFRAMETIME = int(1000/SCREENREFRESHRATE)

#wrong TODO: this
pixPerCm = (DISPSIZE[0] / (2*SCREENSIZE[0])) + (DISPSIZE[1] / (2*SCREENSIZE[1])) 

def DegToPix(deg):
    # tan(10degrees) = radius/distance
    # radius = tan(angle) * distance
    global SCREENDIST, pixPerCm
    rad = deg/360 * math.tau
    dist = math.tan((rad)) * SCREENDIST
    if __name__ == "__main__":
        print(f"ppc={pixPerCm}")
        print(f"tan(rad)={math.tan((rad))}")
        print(f"dist: {pixPerCm * dist * math.tan(rad)}")
    # convert from cm to pixels
    return dist * pixPerCm

#EXPERIMENT INFO
TARGETSIZE = 10 #size of targets
GAZEREGION = DegToPix(3) #extra distance the gaze is allowed to drift from a ROI before the experiment takes action
if __name__ == "__main__":
    print(f'Gazeregion = {GAZEREGION}')
#calculating the radius at which targets will be drawn

TARGETDISTANCE = DegToPix(10)
TARGETAREARADIUS = int(TARGETDISTANCE * 1.05)
FIXATIONSIZE = DegToPix(3)
INTERTIME_CHECKGAZEPOS = 5
FIXATIONTIME = 800
TARTIME = 800
TRIALSPRAC = 10
TRIALS = 100
BLOCKS = 3 #starts at 0 ...
CIRCLEPOLYGONCOUNT = 256


# INPUT
# used in libinput. The values may be adjusted, but not the constant names.
MOUSEBUTTONLIST = None # None for all mouse buttons; list of numbers for buttons of choice (e.g. [1,3] for buttons 1 and 3)
MOUSETIMEOUT = None # None for no timeout, or a value in milliseconds
KEYLIST = None # None for all keys; list of keynames for keys of choice (e.g. ['space','9',':'] for space, 9 and ; keys)
KEYTIMEOUT = 1 # None for no timeout, or a value in milliseconds
JOYBUTTONLIST = None # None for all joystick buttons; list of button numbers (start counting at 0) for buttons of choice (e.g. [0,3] for buttons 0 and 3 - may be reffered to as 1 and 4 in other programs)
JOYTIMEOUT = None # None for no timeout, or a value in milliseconds

# EYETRACKER
# general
TRACKERTYPE = 'eyelink' # either 'smi', 'eyelink' or 'dummy' (NB: if DUMMYMODE is True, trackertype will be set to dummy automatically)
SACCVELTHRESH = 35 # degrees per second, saccade velocity threshold
SACCACCTHRESH = 9500 # degrees per second, saccade acceleration threshold
# EyeLink only
# SMI only
SMIIP = '127.0.0.1'
SMISENDPORT = 4444
SMIRECEIVEPORT = 5555

# FRL
# Used in libgazecon.FRL. The values may be adjusted, but not the constant names.
FRLSIZE = 200 # pixles, FRL-size
FRLDIST = 125 # distance between fixation point and FRL
FRLTYPE = 'gauss' # 'circle', 'gauss', 'ramp' or 'raisedCosine'
FRLPOS = 'center' # 'center', 'top', 'topright', 'right', 'bottomright', 'bottom', 'bottomleft', 'left', or 'topleft'

# CURSOR
# Used in libgazecon.Cursor. The values may be adjusted, but not the constants' names
CURSORTYPE = 'cross' # 'rectangle', 'ellipse', 'plus' (+), 'cross' (X), 'arrow'
CURSORSIZE = 20 # pixels, either an integer value or a tuple for width and height (w,h)
CURSORCOLOUR = 'pink' # colour name (e.g. 'red'), a tuple RGB-triplet (e.g. (255, 255, 255) for white or (0,0,0) for black), or a RGBA-value (e.g. (255,0,0,255) for red)
CURSORFILL = True # True for filled cursor, False for non filled cursor
CURSORPENWIDTH = 3 # cursor edge width in pixels (only if cursor is not filled)
