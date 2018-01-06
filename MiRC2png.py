#!/usr/bin/env python3
#
# MiRC2png.py -- convert ASCII w/ mIRC control codes to monospaced PNG (for EFnet #MiRCART)
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

from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import string, sys

class MiRC2png:
    """Abstraction over ASCIIs containing mIRC control codes"""
    inFilePath = inFile = None;
    inLines = inColsMax = inRows = None;

    outFontFilePath = outFontSize = None;
    outImg = outImgDraw = outImgFont = None;
    outCurColourBg = outCurColourFg = None;
    outCurX = outCurY = None;

    inCurBold = inCurItalic = inCurUnderline = None;
    inCurColourSpec = None;
    state = None;
    inCurCol = inCurDigits = None;

    # {{{ _ColourMapBold: mIRC colour number to RGBA map given ^B (bold)
    _ColourMapBold = [
        (255, 255, 255, 255),   # White
        (85,  85,  85,  255),   # Grey
        (85,  85,  255, 255),   # Light Blue
        (85,  255, 85,  255),   # Light Green
        (255, 85,  85,  255),   # Light Red
        (255, 85,  85,  255),   # Light Red
        (255, 85,  255, 255),   # Pink
        (255, 255, 85,  255),   # Light Yellow
        (255, 255, 85,  255),   # Light Yellow
        (85,  255, 85,  255),   # Light Green
        (85,  255, 255, 255),   # Light Cyan
        (85,  255, 255, 255),   # Light Cyan
        (85,  85,  255, 255),   # Light Blue
        (255, 85,  255, 255),   # Pink
        (85,  85,  85,  255),   # Grey
        (255, 255, 255, 255),   # White
    ]
    # }}}
    # {{{ _ColourMapNormal: mIRC colour number to RGBA map given none of ^[BFV_] (bold, italic, reverse, underline)
    _ColourMapNormal = [
        (255, 255, 255, 255),   # White
        (0,   0,   0,   255),   # Black
        (0,   0,   187, 255),   # Blue
        (0,   187, 0,   255),   # Green
        (255, 85,  85,  255),   # Light Red
        (187, 0,   0,   255),   # Red
        (187, 0,   187, 255),   # Purple
        (187, 187, 0,   255),   # Yellow
        (255, 255, 85,  255),   # Light Yellow
        (85,  255, 85,  255),   # Light Green
        (0,   187, 187, 255),   # Cyan
        (85,  255, 255, 255),   # Light Cyan
        (85,  85,  255, 255),   # Light Blue
        (255, 85,  255, 255),   # Pink
        (85,  85,  85,  255),   # Grey
        (187, 187, 187, 255),   # Light Grey
    ]
    # }}}
    # {{{ _State(Enum): Parsing loop state
    class _State(Enum):
        STATE_CHAR = 1
        STATE_COLOUR_SPEC = 2
        STATE_CSPEC_DIGIT0 = 2
        STATE_CSPEC_DIGIT1 = 3
    # }}}

    # {{{ _countChar(self, char): XXX
    def _countChar(self, char):
        return True
    # }}}
    # {{{ _countColourSpecState(self, colourSpec): XXX
    def _countColourSpecState(self, colourSpec):
        return 0
    # }}}
    # {{{ _render(self): XXX
    def _render(self):
        self.outCurX = 0; self.outCurY = 0;
        for inCurRow in range(0, len(self.inLines)):
            self.inCurBold = 0; self.inCurItalic = 0; self.inCurUnderline = 0;
            self.inCurColourSpec = ""; self._State = self._State.STATE_CHAR;
            self.inCurCol = 0; self.inCurDigits = 0;
            while self.inCurCol < len(self.inLines[inCurRow]):
                if self._State == self._State.STATE_CHAR:
                    self._parseAsChar(                                  \
                        self.inLines[inCurRow][self.inCurCol],          \
                        self._syncChar)
                elif self._State == self._State.STATE_CSPEC_DIGIT0      \
                or   self._State == self._State.STATE_CSPEC_DIGIT1:     \
                    self._parseAsColourSpec(                            \
                        self.inLines[inCurRow][self.inCurCol],          \
                        self._syncColourSpecState)
            self.outCurX = 0; self.outCurY += self.outImgFontSize[1];
    # }}}
    # {{{ _getMaxCols(self, lines): Calculate widest row in lines, ignoring non-printable & mIRC control code sequences
    def _getMaxCols(self, lines):
        maxCols = 0;
        for inCurRow in range(0, len(lines)):
            self.inCurBold = 0; self.inCurItalic = 0; self.inCurUnderline = 0;
            self.inCurColourSpec = ""; self._State = self._State.STATE_CHAR;
            self.inCurCol = 0; self.inCurDigits = 0; curRowCols = 0;
            while self.inCurCol < len(self.inLines[inCurRow]):
                if self._State == self._State.STATE_CHAR:
                    if self._parseAsChar(                               \
                            self.inLines[inCurRow][self.inCurCol], self._countChar):
                        curRowCols += 1
                elif self._State == self._State.STATE_CSPEC_DIGIT0      \
                or   self._State == self._State.STATE_CSPEC_DIGIT1:
                    self._parseAsColourSpec(                            \
                        self.inLines[inCurRow][self.inCurCol],          \
                        self._countColourSpecState)
            maxCols = max(maxCols, curRowCols)
        return maxCols
    # }}}
    # {{{ _parseAsChar(self, char, fn): Parse single character as regular character and mutate state
    def _parseAsChar(self, char, fn):
        if char == "":
            self._State = self._State.STATE_CSPEC_DIGIT0; self.inCurCol += 1;
            return False
        else:
            self.inCurCol += 1; return fn(char);
    # }}}
    # {{{ _parseAsColourSpec(self, char, fn): Parse single character as mIRC colour control code sequence and mutate state
    def _parseAsColourSpec(self, char, fn):
        if  self._State == self._State.STATE_CSPEC_DIGIT0               \
        and char == ",":
            self.inCurColourSpec += char; self.inCurCol += 1;
            self._State = self._State.STATE_CSPEC_DIGIT1;
            self.inCurDigits = 0
            return [False]
        elif self._State == self._State.STATE_CSPEC_DIGIT0              \
        and  char in set("0123456789")                                  \
        and  self.inCurDigits <= 1:
            self.inCurColourSpec += char; self.inCurCol += 1;
            self.inCurDigits += 1
            return [False]
        elif self._State == self._State.STATE_CSPEC_DIGIT1              \
        and  char in set("0123456789")                                  \
        and  self.inCurDigits <= 1:
            self.inCurColourSpec += char; self.inCurCol += 1;
            self.inCurDigits += 1
            return [False]
        else:
            result = fn(self.inCurColourSpec)
            self.inCurColourSpec = ""; self._State = self._State.STATE_CHAR;
            self.inCurDigits = 0
            return [True, result]
    # }}}
    # {{{ _syncChar(self, char): XXX
    def _syncChar(self, char):
        if char == "":
            self.inCurBold = 0 if self.inCurBold else 1;
        elif char == "":
            self.inCurItalic = 0 if self.inCurItalic else 1;
        elif char == "":
            self.inCurBold = 0; self.inCurItalic = 0; self.inCurUnderline = 0;
            self.inCurColourSpec = "";
        elif char == "":
            self.outCurColourBg, self.outCurColourFg = self.outCurColourFg, self.outCurColourBg;
        elif char == "":
            self.inCurUnderline = 0 if self.inCurUnderline else 1;
        elif char == " ":
            if self.inCurBold:
                colourBg = self._ColourMapBold[self.outCurColourBg]
            else:
                colourBg = self._ColourMapNormal[self.outCurColourBg]
            self.outImgDraw.rectangle(((self.outCurX, self.outCurY), (self.outCurX + self.outImgFontSize[0], self.outCurY + self.outImgFontSize[1])), fill=colourBg)
            if self.inCurUnderline:
                self.outImgDraw.line((self.outCurX, self.outCurY + (self.outImgFontSize[1] - 2), self.outCurX + self.outImgFontSize[0], self.outCurY + (self.outImgFontSize[1] - 2)), fill=colourFg)
            self.outCurX += self.outImgFontSize[0];
        else:
            if self.inCurBold:
                colourBg = self._ColourMapBold[self.outCurColourBg]
                colourFg = self._ColourMapBold[self.outCurColourFg]
            else:
                colourBg = self._ColourMapNormal[self.outCurColourBg]
                colourFg = self._ColourMapNormal[self.outCurColourFg]
            self.outImgDraw.rectangle(((self.outCurX, self.outCurY), (self.outCurX + self.outImgFontSize[0], self.outCurY + self.outImgFontSize[1])), fill=colourBg)
            # XXX implement italic
            self.outImgDraw.text((self.outCurX, self.outCurY), char, colourFg, self.outImgFont)
            if self.inCurUnderline:
                self.outImgDraw.line((self.outCurX, self.outCurY + (self.outImgFontSize[1] - 2), self.outCurX + self.outImgFontSize[0], self.outCurY + (self.outImgFontSize[1] - 2)), fill=colourFg)
            self.outCurX += self.outImgFontSize[0];
        return True
    # }}}
    # {{{ _syncColourSpecState(self, colourSpec): XXX
    def _syncColourSpecState(self, colourSpec):
        if len(colourSpec) > 0:
            colourSpec = colourSpec.split(",")
            if len(colourSpec) == 2:
                self.outCurColourFg = int(colourSpec[0])
                self.outCurColourBg = int(colourSpec[1] or self.outCurColourBg)
            elif len(colourSpec) == 1:
                self.outCurColourFg = int(colourSpec[0])
            else:
                self.outCurColourBg = 1; self.outCurColourFg = 15;
        return True
    # }}}

    #
    # __init__(self, inFilePath, imgFilePath, fontFilePath="DejaVuSansMono.ttf", fontSize=11): initialisation method
    def __init__(self, inFilePath, imgFilePath, fontFilePath="DejaVuSansMono.ttf", fontSize=11):
        self.inFilePath = inFilePath; self.inFile = open(inFilePath, "r");
        self.inLines = self.inFile.readlines()
        self.inColsMax = self._getMaxCols(self.inLines)
        self.inRows = len(self.inLines)
        self.outFontFilePath = fontFilePath; self.outFontSize = int(fontSize);
        self.outImgFont = ImageFont.truetype(self.outFontFilePath, self.outFontSize)
        self.outImgFontSize = list(self.outImgFont.getsize(" ")); self.outImgFontSize[1] += 3;
        self.outImg = Image.new("RGBA", (self.inColsMax * self.outImgFontSize[0], self.inRows * self.outImgFontSize[1]), self._ColourMapNormal[1])
        self.outImgDraw = ImageDraw.Draw(self.outImg)
        self.outCurColourBg = 1; self.outCurColourFg = 15;
        self._render()
        self.inFile.close();
        self.outImg.save(imgFilePath);

#
# Entry point
def main(*argv):
    MiRC2png(*argv[1:])
if __name__ == "__main__":
    if ((len(sys.argv) - 1) < 2)\
    or ((len(sys.argv) - 1) > 4):
        print("usage: {} "                                              \
            "<MiRCART input file pathname> "                            \
            "<PNG image output file pathname> "                         \
            "[<Font file pathname; defaults to DejaVuSansMono.ttf>] "   \
            "[<Font size; defaults to 11>]".format(sys.argv[0]), file=sys.stderr)
    else:
        main(*sys.argv)

# vim:expandtab foldmethod=marker sw=4 ts=4 tw=120
