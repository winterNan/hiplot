import os
import matplotlib.pyplot as plt
import hashlib
from matplotlib.backends.backend_pdf import PdfPages
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

    def __init__(self, SN):
        self._wc = wow_color()
        self.SN = SN

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
                        xtickon,
                        stack = False,
                        style = "bar",
                        iname="",
                        legendon=False):
        ax.yaxis.grid(True)
        ax.yaxis.grid(color='black', linestyle='dotted', zorder=0)

        if stack == False:
            groups = self.mk_groups(data)
            xy = groups.pop()
            x, y = zip(*xy)
            ly = len(y)
            xticks = range(1, ly + 1)

            if style == "bar":
                ax.bar(xticks, y, align='center',
                       color=[self._wc(item) for item in x],
                       edgecolor='black', zorder=3)
            elif style == "line":
                ax.plot(xticks, y, zorder=3,
                        label=iname, color=COLOR[iname],
                        linewidth=3)
            else:
                sys.exit()
        else:
            for i in data.keys():
                groups = mk_groups(data[i])
                xy = groups.pop()
                x, y = zip(*xy)
                ly = len(y)
                if i == list(data.keys())[0]:
                    bot = [0] * ly
                xticks = range(1, ly + 1)
                ax.bar(xticks, y, bottom = bot, label=self.SN[i],
                       align='center',
                       color= self._wc(i),
                       edgecolor='black',
                       zorder=3)
                bot = [x+y for x,y in zip(bot, y)]

        if legendon == True:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.4, 0, 0),
                      ncol=9, edgecolor='black')

        if xtickon == True:
            ax.set_xticks(xticks)
            ax.set_xticklabels(x, rotation=90)
            ax.set_xlim(.5, ly + .5)

            scale = 1. / ly
            for pos in range(ly + 1):  # change xrange to range for python3
                self.add_line(ax, pos * scale, -0.05, 0.05)
            ypos = -.6
            while groups:
                group = groups.pop()
                pos = 0
                for label, rpos in group:
                    for sn in self.SN.keys():
                        if sn in label:
                            label = label.replace(sn, self.SN[sn])
                            break
                    lxpos = (pos + .5 * rpos) * scale
                    ax.text(lxpos, ypos, label, ha='center',
                            transform=ax.transAxes)
                    self.add_line(ax, pos * scale, -0.6, 0.6)
                    pos += rpos
                self.add_line(ax, pos * scale, ypos, 0.6)
                ypos -= .1
        else:
            ax.set_xticks(xticks)
            ax.set_xticklabels([])
            ax.set_xlim(.5, ly + .5)

    def do_plot1(self,
                 dir_name, name, y_title,
                 data,
                 percentage = False,
                 stack = False,
                 width = 30,
                 start = 0,
                 end = 1.0,
                 step = 0.1):
        isExist = os.path.exists(dir_name)
        if not isExist:
            os.makedirs(dir_name)

        print(bcolors.GREEN + dir_name + name + '.pdf' + bcolors.ENDC)
        fig = plt.figure(figsize=(width, 2))
        pp = PdfPages(dir_name + '/' + name + '.pdf')
        ax = fig.add_subplot(1,1,1)
        self.label_group_bar(ax, data, True, stack)
        fig.subplots_adjust(bottom=0.3)
        ax.set_ylabel(y_title)

        if percentage is True:
            ax.set_ylim([start, end*1.1])
            ax.set_yticks(np.arange(start, end*1.1, step))
            ax.set_yticklabels(str(int(x*100)) + '%' \
                               for x in np.arange(start, end*1.1, step))

        plt.savefig(pp, format='pdf', bbox_inches='tight')
        pp.close()
