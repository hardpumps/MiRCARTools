#!/usr/bin/env python3
#
# MiRCARTToolRect.py -- XXX
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

class MiRCARTToolRect(MiRCARTTool):
    """XXX"""

    #
    # onMouseEvent(self, event, mapPoint, isDragging, isLeftDown, isRightDown): XXX
    def onMouseEvent(self, event, mapPoint, isDragging, isLeftDown, isRightDown):
        if isLeftDown:
            return [[False, [[0, 0,                 \
                self.parentCanvas.mircFg,           \
                self.parentCanvas.mircFg, " "]]],
                    [True, [[0, 0,                  \
                self.parentCanvas.mircFg,           \
                self.parentCanvas.mircFg, " "]]]]
        elif isRightDown:
            return [[False, [[0, 0,                 \
                self.parentCanvas.mircBg,           \
                self.parentCanvas.mircBg, " "]]],   \
                    [True, [[0, 0,                  \
                self.parentCanvas.mircBg,           \
                self.parentCanvas.mircBg, " "]]]]
        else:
            return [[True, [[0, 0,                  \
                self.parentCanvas.mircFg,           \
                self.parentCanvas.mircFg, " "]]]]

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120