#!/usr/bin/env python3
#
# MiRCARTToolText.py -- XXX
# Copyright (c) 2018 Lucio Andrés Illanes Albornoz <lucio@lucioillanes.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from MiRCARTTool import MiRCARTTool
import wx

class MiRCARTToolText(MiRCARTTool):
    """XXX"""
    name = "Text"
    textColours = textPos = None

    #
    # onKeyboardEvent(self, event, atPoint, brushColours, brushSize, keyChar, dispatchFn, eventDc): XXX
    def onKeyboardEvent(self, event, atPoint, brushColours, brushSize, keyChar, dispatchFn, eventDc):
        keyModifiers = event.GetModifiers()
        if  keyModifiers != wx.MOD_NONE     \
        and keyModifiers != wx.MOD_SHIFT:
            return True
        else:
            if self.textColours == None:
                self.textColours = brushColours.copy()
            if self.textPos == None:
                self.textPos = list(atPoint)
        dispatchFn(eventDc, False, [*self.textPos, *self.textColours, 0, keyChar])
        if self.textPos[0] < (self.parentCanvas.canvasSize[0] - 1):
            self.textPos[0] += 1
        elif self.textPos[1] < (self.parentCanvas.canvasSize[1] - 1):
            self.textPos[0] = 0
            self.textPos[1] += 1
        else:
            self.textPos = [0, 0]
        return False

    #
    # onMouseEvent(self, event, atPoint, brushColours, brushSize, isDragging, isLeftDown, isRightDown, dispatchFn, eventDc): XXX
    def onMouseEvent(self, event, atPoint, brushColours, brushSize, isDragging, isLeftDown, isRightDown, dispatchFn, eventDc):
        if isLeftDown:
            self.textColours = brushColours.copy()
            self.textPos = list(atPoint)
        elif isRightDown:
            self.textColours = [brushColours[1], brushColours[0]]
            self.textPos = list(atPoint)
        else:
            if self.textColours == None:
                self.textColours = brushColours.copy()
            self.textPos = list(atPoint)
        dispatchFn(eventDc, True, [*self.textPos, *self.textColours, 0, "_"])

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
