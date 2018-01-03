#!/usr/bin/env python3
#
# mirc2png -- convert ASCII w/ mIRC control codes to monospaced PNG (for EFnet #MiRCART)
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

class MiRCART:
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
    inCurCol = None;

    # {{{ ColourMapBold: mIRC colour number to RGBA map given ^B (bold)
    ColourMapBold = [
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
    # {{{ ColourMapNormal: mIRC colour number to RGBA map given none of ^[BFV_] (bold, italic, reverse, underline)
    ColourMapNormal = [
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
    # {{{ State: Parsing loop state
    class State(Enum):
        STATE_CHAR = 1
        STATE_COLOUR_SPEC = 2
    # }}}

    # {{{ getMaxCols(): Calculate widest row in lines, ignoring non-printable & mIRC control code sequences
    def getMaxCols(self, lines):
        maxCols = 0;
        for curRow in range(0, len(lines)):
            curRowCols = 0; curState = self.State.STATE_CHAR;
            curCol = 0; curColLen = len(lines[curRow]);
            while curCol < curColLen:
                curChar = lines[curRow][curCol]
                if curState == self.State.STATE_CHAR:
                    if curChar == "":
                        curState = self.State.STATE_COLOUR_SPEC; curCol += 1;
                    elif curChar in string.printable:
                        curRowCols += 1; curCol += 1;
                    else:
                        curCol += 1;
                elif curState == self.State.STATE_COLOUR_SPEC:
                    if curChar in set(",0123456789"):
                        curCol += 1;
                    else:
                        curState = self.State.STATE_CHAR;
            maxCols = max(maxCols, curRowCols)
        return maxCols
    # }}}
    # {{{ parseAsChar(): Parse single character as regular character and mutate state
    def parseAsChar(self, char):
            if char == "":
                self.inCurCol += 1; self.inCurBold = 0 if self.inCurBold else 1;
            elif char == "":
                self.state = self.State.STATE_COLOUR_SPEC; self.inCurCol += 1;
            elif char == "":
                self.inCurCol += 1; self.inCurItalic = 0 if self.inCurItalic else 1;
            elif char == "":
                self.inCurCol += 1;
                self.inCurBold = 0; self.inCurItalic = 0; self.inCurUnderline = 0;
                self.inCurColourSpec = "";
            elif char == "":
                self.inCurCol += 1
                self.outCurColourBg, self.outCurColourFg = self.outCurColourFg, self.outCurColourBg;
            elif char == "":
                self.inCurCol += 1; self.inCurUnderline = 0 if self.inCurUnderline else 1;
            elif char == " ":
                if self.inCurBold:
                    colourBg = self.ColourMapBold[self.outCurColourBg]
                else:
                    colourBg = self.ColourMapNormal[self.outCurColourBg]
                self.outImgDraw.rectangle(((self.outCurX, self.outCurY), (self.outCurX + 7, self.outCurY + 14)), fill=colourBg)
                if self.inCurUnderline:
                    self.outImgDraw.line((self.outCurX, self.outCurY + 11, self.outCurX + 7, self.outCurY + 11), fill=colourFg)
                self.outCurX += 7; self.inCurCol += 1;
            else:
                if self.inCurBold:
                    colourBg = self.ColourMapBold[self.outCurColourBg]
                    colourFg = self.ColourMapBold[self.outCurColourFg]
                else:
                    colourBg = self.ColourMapNormal[self.outCurColourBg]
                    colourFg = self.ColourMapNormal[self.outCurColourFg]
                self.outImgDraw.rectangle(((self.outCurX, self.outCurY), (self.outCurX + 7, self.outCurY + 14)), fill=colourBg)
                # XXX implement italic
                self.outImgDraw.text((self.outCurX, self.outCurY), char, colourFg, self.outImgFont)
                if self.inCurUnderline:
                    self.outImgDraw.line((self.outCurX, self.outCurY + 11, self.outCurX + 7, self.outCurY + 11), fill=colourFg)
                self.outCurX += 7; self.inCurCol += 1;
    # }}}
    # {{{ parseAsColourSpec(): Parse single character as mIRC colour control code sequence and mutate state
    def parseAsColourSpec(self, char):
            if char in set(",0123456789"):
                self.inCurColourSpec += char; self.inCurCol += 1;
            else:
                self.inCurColourSpec = self.inCurColourSpec.split(",")
                if len(self.inCurColourSpec) == 2:
                    self.outCurColourFg = int(self.inCurColourSpec[0])
                    self.outCurColourBg = int(self.inCurColourSpec[1] or self.outCurColourBg)
                elif len(self.inCurColourSpec) == 1:
                    self.outCurColourFg = int(self.inCurColourSpec[0])
                else:
                    self.outCurColourBg = 1; self.outCurColourFg = 15;
                self.inCurColourSpec = ""; self.state = self.State.STATE_CHAR;
    # }}}

    #
    # Initialisation method
    def __init__(self, inFilePath, imgFilePath, fontFilePath="DejaVuSansMono.ttf", fontSize=11):
        self.inFilePath = inFilePath; self.inFile = open(inFilePath, "r");
        self.inLines = self.inFile.readlines()
        self.inColsMax = self.getMaxCols(self.inLines)
        self.inRows = len(self.inLines)
        self.outFontFilePath = fontFilePath; self.outFontSize = int(fontSize);
        self.outImg = Image.new("RGBA", (self.inColsMax * 7, self.inRows * 14), self.ColourMapNormal[1])
        self.outImgDraw = ImageDraw.Draw(self.outImg)
        self.outImgFont = ImageFont.truetype(self.outFontFilePath, self.outFontSize)
        self.outCurColourBg = 1; self.outCurColourFg = 15;
        self.outCurX = 0; self.outCurY = 0;
        for inCurRow in range(0, len(self.inLines)):
            self.inCurBold = 0; self.inCurItalic = 0; self.inCurUnderline = 0;
            self.inCurColourSpec = ""; self.state = self.State.STATE_CHAR;
            self.inCurCol = 0;
            while self.inCurCol < len(self.inLines[inCurRow]):
                if self.state == self.State.STATE_CHAR:
                    self.parseAsChar(self.inLines[inCurRow][self.inCurCol])
                elif self.state == self.State.STATE_COLOUR_SPEC:
                    self.parseAsColourSpec(self.inLines[inCurRow][self.inCurCol])
            self.outCurX = 0; self.outCurY += 13;
        self.inFile.close();
        self.outImg.save(imgFilePath);

#
# Entry point
def main(*argv):
    _MiRCART = MiRCART(*argv[1:])
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

# vim:expandtab foldmethod=marker sw=8 ts=8 tw=120