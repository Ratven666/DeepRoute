from matplotlib import pyplot as plt


class OilWellPlotterMPL:

    def __init__(self, fig_ax=None, is_show=True):
        self.fig, self.ax = fig_ax if fig_ax is not None else (None, None)
        self.is_show = is_show

    def plot(self, oil_well):
        if self.ax is None:
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(projection='3d')
        x, y, z, c = ([oil_well.start_point.x],
                      [oil_well.start_point.y],
                      [oil_well.start_point.z],
                      [1])
        for section in oil_well:
            for subsection in section:
                x.append(subsection.end_point.x)
                y.append(subsection.end_point.y)
                z.append(subsection.end_point.z)
                c.append(subsection.number)


        self.ax.scatter(x, y, z, c=c)
        self.ax.set_xlabel('Y')
        self.ax.set_ylabel('X')
        plt.axis('equal')
        if self.is_show:
            plt.show()
        return self.fig, self.ax
