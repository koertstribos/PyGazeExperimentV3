from ast import Lambda
from asyncio.windows_events import NULL
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import libinput
from pygaze import eyetracker


from typing import Callable




class Screen():
    def __init__(self, gazeContingency, screen = None):
        if isinstance(screen, libscreen.Screen):
            self.screen = screen
        elif isinstance(screen, str):
            self.screen = libscreen.Screen()
            self.screen.draw_text(text=screen, fontsize=24)
        else:
            self.screen = libscreen.Screen()
        self.Rules = []
        self.GC = gazeContingency

    def AddRule(self, rule, target):
        self.Rules.append([rule,target])

    def CallRules(self, frameStart):
        for rule, target in self.Rules:
            if rule.Evaluate(frameStart):
                if isinstance(target, str):
                    return self.GC.GotoScreen(target)
                elif isinstance(target, Callable):
                    return target()

 
    #func replaceScreen
    #replaces the libscreen.Screen coupled to a GC Screen
    #useful for looping over multiple trials with the same rules
    #args:
    #       screen: GazeContingency.Screen object OR libscreen.Screen object OR string
    #
    #

    def ReplaceScreen(self, screen):

        if isinstance(screen, libscreen.Screen):
            self.screen = screen
        elif isinstance(screen, str):
            stringScreen = libscreen.Screen()
            stringScreen.draw_text(text=screen, fontsize = 24)
            self.screen = stringScreen
        else:
            try:
                self.screen = screen.screen
            except: Exception(f"{screen} is not a GazeContingency Screen, Pygaze.libscreen Screen, or string ")

    def __str__(self):
        return self.GC.ReturnScreenString(self)



#class Rule:
#saves a reference to a function, and Evaluates the function when called by the GazeContingentScreen
#is coupled to two screens by the AddRule function called from a GazeContingentScreen
class Rule:
    def __init__(self, interval: int, func:Callable[[], bool]):
        self.f = func
        self.interval = interval
        self.nextCall = 0

    #no function description
    #TODO:  move this evaluation to GCScreen
    #           add parallel timing (e.g.) for ruleTime in ruleTimes: if ruleTime.nextCall > time: ruleTime.evaluate()
    #           because optimalisation is life
    def Evaluate(self, time):
        if time > self.nextCall:
            self.nextCall = time + self.interval
            return self._Evaluate()

    def _Evaluate(self):
        res = self.f()
        return(res)



class GazeContingency:
    def __init__(self, display: libscreen.Display, eyetracker: eyetracker.EyeTracker, keyboard: libinput.Keyboard, framerate, pauseOnBlink = True, copy_libinput_Keyboard_defaultkeys = True):

        self.disp = display
        self.track = eyetracker
        self.keyb = keyboard
        self.loop = True
        
        self.timeOnScreen = 0
        self.pauseOnBlink = pauseOnBlink
        self.framerate = framerate
        self.frameTime = 1000/framerate

        self.screens = {}
        self.screenCurrent = None

        self.rules = []
        self.keysToCheck = []
        if copy_libinput_Keyboard_defaultkeys:

            for key in self.keyb.klist:
                print(f"adding {key} to GazeContingency.keysToCheck")
                self.keysToCheck.append(key)
        self.keys = []



    def SetKeysCheck(self, keylist):
        self.keysToCheck = keylist

    def AddKeyCheck(self, key):
        self.keysToCheck.append(key)

    def GetLastKey(self):
        return(self.keys[-1])

    def _Flush(self, key, target):
        if target == 'all':
            for key in self.keysToCheck:
                self.Flush(key)
        elif target =="self":
            self.Flush(key)

    def Flush(self, targets):
        #botch
        if isinstance(targets, str):
            targets = [targets]

        for target in targets:
            while target in self.keys:
                self.keys.remove(target)


    #arg:
    #      reset:   'self': resets found key on find
    #               'all':  resets all keys on find
    #               'none:  doesn't reset keys on find
    #               *   :   doesn't reset keys on find

    def GetIfKey(self, keys, depth=None, reset = "self"):
        #botch
        if isinstance(keys, str):
            keys = [keys]
        # check if all keys are in self.keystocheck
        for key in keys:
            if not key in self.keysToCheck:
                print(f"looking whether {key} has been pressed, but this key is not being saved on press.")
                print("please use GazeContingency.SetKeysCheck, or GazeContingency.AddKeyCheck()")

        if isinstance(depth, int):
            return self._GetIfKey_Depth(keys, depth, reset)
        else:
            return self._GetIfKey_NoDepth(keys, reset)


    def _GetIfKey_FlushTrue(self, key, reset):
        self._Flush(key, reset)
        return True

    def _GetIfKey_NoDepth(self, keys, reset):

        for key in keys:
            for sKey in self.keys:
                if key == sKey:
                    return self._GetIfKey_FlushTrue(key, reset)

        return False

    def _GetIfKey_Depth(self, keys, depth, reset):

        for key in keys:
            for d in range(depth):
                if self.keys[-d]==key:
                    return self._GetIfKey_FlushTrue(key, reset)
        return False



    def GetKeylist(self, flipped=True):
        if not flipped:
            return self.keys
        else:
            fkeys = []
            for key in self.keys:
                fkeys.append(key)


    def Loop(self, libTime, startingScreen):
        self.GotoScreen(startingScreen)

        startTime = libTime.get_time()
        frameStart = startTime
        while(self.loop):

            frameStart = libTime.get_time()
            self.CallRules(frameStart)

            frameTime = libTime.get_time() - frameStart

            if frameTime > self.frameTime:
                self.IncrTime(frameTime)

            else:
                libTime.pause(self.frameTime - frameTime)
                self.IncrTime(self.frameTime)


    
    def IncrTime(self, time):
        if not (self.pauseOnBlink and self.Blink()):
            self.timeOnScreen += time
            
    def Blink(self):
        return self.track.sample() == (-1,-1)


    #function for adding a screen. 
    #args:
    #   screen:     PyGaze.libscreen.Screen object
    #   screentype: string
    #               one of the allowed screens from dict screenTypes

    def AddScreen(self, screen, screentype):
        if screentype in self.screens:
            self.screens[screentype].ReplaceScreen(screen)
        else:
            if isinstance(screen, libscreen.Screen):
                self.screens[screentype] = Screen(self, screen)

            elif isinstance(screen, str):
                self.screens[screentype] = Screen(self, screen)
            else:
                try:
                    self.screens[screentype] = screen 
                except: Exception(f"{screen} is not a GazeContingency Screen, Pygaze.libscreen Screen, or string ")
    

    #function for adding rules
    #args:
    #   at_screen:          Reference to the screen on which this rule is to be evaluated.
    #                       if "any", rule is evaluated every frame regardless of Screen
    #   goto_screen:        dict key for the Screen that is switched to on succesful result of rule evaluation 
    #                    OR callable function that is called on succesful result of rule evaluation 
    #   when_rule:          GazeContingency.Rule object
    def AddRule(self, target_screen_or_command, when_rule, at_screen='any'):
        rule = when_rule
        target = target_screen_or_command
        screenType = at_screen

        if isinstance(screenType, str):
            if screenType == 'any':
                self.rules.append([rule, target])
            elif screenType in self.screens:
                self.screens[screenType].AddRule(rule, target)

        else:
            Exception("AddRule")

    def CallRules(self, time):
        #fetch keypress
        key = self.keyb.get_key(keylist=self.keysToCheck, timeout=1)[0]
        if key != None:
            self.keys.append(key)

        #call all rules coupled to the GC obj
        for rule, target in self.rules:
            if rule.Evaluate(time):
                if isinstance(target, str):
                    self.GotoScreen(target)
                if isinstance(target, Callable):
                    return target()
        #call all rules coupled to the current screen
        self.screenCurrent.CallRules(time)

    #function for getting a Screen object, even if it does not exist
    def Screen(self, screenType):
        if screenType in self.screens:
            return self.screens[screenType]
        else:
            try:
                tempScreen = libscreen.Screen()
                tempScreen.draw_text(text=f"{screenType}", fontsize=24)
                return Screen(self, tempScreen)
            except:
                tempScreen = libscreen.Screen()
                print("GazeContingency.Screen error")
                tempScreen.draw_text(text=f"error: {screenType} is not a string", fontsize=24)
                return Screen(self, tempScreen)


    def GotoScreen(self, screenType: str, final = False):
        if final:
            self.loop = False

        self.track.log("S: showing screen %s" % screenType)
        self.timeOnScreen = 0
        self.screenCurrent = self.Screen(screenType)
        self.disp.fill(self.screenCurrent.screen)
        self.disp.show()

    def ReturnScreenString(self, screen):
        for key, value in self.screens.items():
            if value == screen:
                return key

    def CurrentScreenKey(self):
        return str(self.screenCurrent)

    def __str__(self):
        return("GazeContingency Object")

    def __repr__(self):
        return("GazeContingency Object @ screen {self.CurrentScreenKey()}")



