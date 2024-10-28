# Filename: plotCPU.py
# Description:
# Author: Yuan Yao <yuan.yao@it.uu.se>
# Maintainer:
# Created: Sun Oct 27 10:53:28 2024 (+0100)
# Version:
# Package-Requires: ()
# Last-Updated:
#           By:
#     Update #: 0
# URL:
# Doc URL:
# Keywords:
# Compatibility:
#
#

import os
import matplotlib.pyplot as plt
import hashlib
from matplotlib.backends.backend_pdf import PdfPages
import json
import numpy as np
from colorama import Fore, Back, Style
plt.rc('font', size=10)


class bcolors:
    RED       = '\033[31m'
    BLUE      = '\033[94m'
    CYAN      = '\033[36m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    MAGENTA   = '\033[35m'
    HEADER    = '\033[35m'
    WARNING   = '\033[33m'
    FAIL      = '\033[31m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


class wow_color:
    def __init__(self):
        _color = {
            'DK'      : '#C41E3A',
            'DH'      : '#A330C9',
            'Druid'   : '#FF7C0A',
            'Hunter'  : '#AAD372',
            'Mage'    : '#3FC7EB',
            'Monk'    : '#00FF98',
            'Paladin' : '#F48CBA',
            'Priset'  : '#FFFFFF',
            'Rougue'  : '#FFF468',
            'Shaman'  : '#0070DD',
            'Warlock' : '#8788EE',
            'Warrior' : '#C69B6D',
            'Evoker'  : '#33937F'
        }
        self._color = _color

    def __call__(self, i):
        nm = -1
        if type(i).__name__ == 'str':
            _i = str.encode(i)
            nm = int(hashlib.sha256(_i).hexdigest(), base=16) % len(self._color.items())
        elif type(i).__name == 'int':
            nm = i % len(self._color.items())

        return self._color[list(self._color.keys())[nm]]


class hiplot:

    def __init__(self, SN=None, color=None):
        self._wc = wow_color()
        self.SN = SN
        self.color = color

    def add_line(self, ax, xpos, ypos, length, style="bar"):
        line = plt.Line2D([xpos, xpos], [ypos + length, ypos],
                          transform=ax.transAxes, color='black')
        line.set_clip_on(False)
        ax.add_line(line)

    def mk_groups(self, data):
        try:
            newdata = data.items()
        except:
            return

        thisgroup = []
        groups = []
        for key, value in newdata:
            newgroups = self.mk_groups(value)
            if newgroups is None:
                thisgroup.append((key, value))
            else:
                thisgroup.append((key, len(newgroups[-1])))
                if groups:
                    groups = [g + n for n, g in zip(newgroups, groups)]
                else:
                    groups = newgroups
        return [thisgroup] + groups

    def label_group_bar(self,
                        ax,
                        data,
                        bar = 0.3,
                        xtickon = True,
                        xinnertickon = True,
                        stack = False,
                        edgecolor = None,
                        style = "bar",
                        iname="",
                        legendon=False,
                        legendloc=None,
                        legendbox=None,
                        gridlinestyle='-',
                        yoffset=1.0,
                        lncol=1,
                        lfont=10):
        ax.yaxis.grid(True)
        ax.yaxis.grid(color='lightgrey',
                      linestyle=gridlinestyle,
                      zorder=0,
                      linewidth=.5)

        if stack == False:
            groups = self.mk_groups(data)
            xy = groups.pop()
            x, y = zip(*xy)
            ly = len(y)
            xticks = range(1, ly + 1)

            if style == "bar":
                if self.color is None:
                    cmap = [self._wc(item) for item in x]
                else:
                    cmap = []
                    for e in x:
                        # TODO what if _ is a string
                        if e == "seperator":
                            cmap.append('white')
                            continue
                        cmap.append(self.color[int(e) % len(self.color)])

                ax.bar(xticks, y, align='center',
                       color = cmap,
                       edgecolor=edgecolor,
                       zorder=3)

            elif style == "line":
                ax.plot(xticks, y, zorder=3,
                        label=iname, color=COLOR[iname],
                        linewidth=3)
            else:
                sys.exit()
        else:
            for i,item in enumerate(list(data.keys())):
                groups = self.mk_groups(data[item])
                xy = groups.pop()
                x, y = zip(*xy)
                ly = len(y)
                if item == list(data.keys())[0]:
                    bot = [0] * ly
                xticks = range(1, ly + 1)

                if self.color is None:
                    cmap = self._wc(item)
                else:
                    cmap = self.color[i]

                ax.bar(xticks, y, bottom = bot,
                       label=self.SN[item],
                       align = 'center',
                       color = cmap,
                       edgecolor = edgecolor,
                       zorder = 3)
                bot = [x+y for x,y in zip(bot, y)]

        if legendon == True:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(
                handles[::-1],
                labels[::-1],
                loc=legendloc,
                bbox_to_anchor=legendbox,
                ncol=lncol,
                edgecolor='black',
                fontsize=lfont)

        if xtickon == True:
            ax.set_xticks(xticks)
            ax.set_xlim(.5, ly + .5)
            if xinnertickon:
                ax.set_xticklabels(x,
                                   fontsize=lfont,
                                   rotation=90)
                # first level x-ticklabel position
                ypos = -bar
            else:
                ax.set_xticklabels([], minor=False)
                # first level x-ticklabel position
                ypos = -bar*0.7

            scale = 1. / ly
            # for pos in range(ly + 1):
            #     # change xrange to range for python3
            #     self.add_line(ax, pos * scale, -0.05, 0.05)
            while groups:
                group = groups.pop()
                pos = 0
                for label, rpos in group:
                    if self.SN != None:
                        for sn in self.SN.keys():
                            if sn in label:
                                label = label.replace(sn, self.SN[sn])
                                break
                    lxpos = (pos + .5 * rpos) * scale # horizontal shift
                    # space between cat label and sub-cat label
                    ax.text(lxpos, ypos-yoffset, label, ha='center',
                            transform=ax.transAxes)
                    self.add_line(ax, pos * scale, -bar*0.8, bar*0.8)
                    pos += rpos
                self.add_line(ax, pos * scale, ypos, bar)
                ypos -= 0.5
        else:
            ax.set_xticks(xticks)
            ax.set_xticklabels([])
            ax.set_xlim(.5, ly + .5)

    @classmethod
    def dictDump(self, _dict, header=" ", percent=False):

        def to_percentage(nested_dict):
            for key, value in nested_dict.items():
                if isinstance(value, dict):
                    # Recursively call the function if the value is another dictionary
                    to_percentage(value)
                else:
                    # Convert the value to a percentage (assuming it's a number)
                    nested_dict[key] = f"{value * 100:.2f}%"
            return nested_dict

        if percent:
            _dict = to_percentage(_dict)

        print(Fore.GREEN + "======" + header + "======" + Style.RESET_ALL)
        print(json.dumps(
            _dict,
            sort_keys=False,
            indent=4,
            separators=(',', ': ')
            )
        )

    def do_plot1(self,
                 dir_name, name, y_title,
                 data,
                 percentage    = False,
                 stack         = False,
                 xtickon       = True,
                 xinnertickon  = True,
                 edgecolor     = None,
                 legendon      = False,
                 legendloc     = None,
                 legendbox     = None,
                 width         = 30,
                 height        = 2,
                 bar           = 0.3,
                 start         = 0,
                 end           = 1.0,
                 step          = 0.1,
                 ytitlesize    = 12,
                 yticksize     = 12,
                 gridlinestyle = '--',
                 yoffset       = 1.0,
                 lncol         = 1,
                 lfont         = 10):
        isExist = os.path.exists(dir_name)
        if not isExist:
            os.makedirs(dir_name)

        print(bcolors.GREEN + dir_name + name + '.pdf' + bcolors.ENDC)
        fig = plt.figure(figsize=(width, height))
        pp = PdfPages(dir_name + '/' + name + '.pdf')
        ax = fig.add_subplot(1,1,1)
        self.label_group_bar(ax,
                             data,
                             bar,
                             xtickon,
                             xinnertickon,
                             stack,
                             edgecolor=edgecolor,
                             legendon=legendon,
                             legendloc=legendloc,
                             legendbox=legendbox,
                             gridlinestyle=gridlinestyle,
                             yoffset=yoffset,
                             lncol=lncol,
                             lfont=lfont)
        fig.subplots_adjust(bottom=0.3)
        ax.set_ylabel(y_title, fontsize=ytitlesize)
        if (xinnertickon == False) or (xtickon == False):
            ax.xaxis.set_ticks_position('none')

        if percentage is True:
            ax.set_ylim([start, end*1.1])
            ax.set_yticks(np.arange(start, end*1.1, step))
            ax.set_yticklabels([str(int(x*100)) + '%' \
                               for x in np.arange(start, end*1.1, step)],
                               fontsize=yticksize)

        plt.savefig(pp, format='pdf', bbox_inches='tight')
        pp.close()
