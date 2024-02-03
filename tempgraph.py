import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import flet as ft
from flet.matplotlib_chart import MatplotlibChart

matplotlib.use("svg")

class tempGraph(ft.UserControl):
    def __init__(self):
        super().__init__(self)
        #追加したプロパティ
        self.counter = 0 
        self.on_countup = lambda: None
        
        self.fig, self.axs = plt.subplots()
        
        # 折れ線グラフを出力
        self.x = np.array([])
        self.y1 = np.array([])
        self.y2 = np.array([])
        self.y3 = np.array([])
        self.y4 = np.array([])
        self.y5 = np.array([])
        self.axs.plot(self.x, self.y1, color="k", label="temp")
        self.axs.plot(self.x, self.y2, color="b", label="a0")
        self.axs.plot(self.x, self.y3, color="r", label="a1")
        self.axs.plot(self.x, self.y4, color="g", label="a2")
        self.axs.plot(self.x, self.y5, color="m", label="a3")
        self.axs.set_xlabel("time")
        self.axs.set_ylabel("temp[℃]")
        self.axs.grid(True)
        self.axs.legend(loc="lower left", fontsize=8) # (3)凡例表示
        
    async def set(self, time, temp, pressure, humidity, altitude, a0, a1, a2, a3):
        self.axs.cla()
        self.x = np.array(time)
        self.y1 = np.array(temp)
        self.y2 = np.array(a0)
        self.y3 = np.array(a1)
        self.y4 = np.array(a2)
        self.y5 = np.array(a3)
        self.axs.plot(self.x, self.y1, color="k", label="temp")
        self.axs.plot(self.x, self.y2, color="b", label="a0")
        self.axs.plot(self.x, self.y3, color="r", label="a1")
        self.axs.plot(self.x, self.y4, color="g", label="a2")
        self.axs.plot(self.x, self.y5, color="m", label="a3")
        self.axs.set_xlabel("time")
        self.axs.set_ylabel("temp[℃]")
        self.axs.grid(True)
        self.axs.legend(loc="lower left", fontsize=8) # (3)凡例表示
        await self.update_async()

    async def reset(self):
        self.axs.cla()

        # self.fig, self.axs = plt.subplots()
        self.x = np.array([])
        self.y1 = np.array([])
        self.y2 = np.array([])
        self.y3 = np.array([])
        self.y4 = np.array([])
        self.y5 = np.array([])
        self.axs.plot(self.x, self.y1, color="k", label="temp")
        self.axs.plot(self.x, self.y2, color="b", label="a0")
        self.axs.plot(self.x, self.y3, color="r", label="a1")
        self.axs.plot(self.x, self.y4, color="g", label="a2")
        self.axs.plot(self.x, self.y5, color="m", label="a3")
        self.axs.set_xlabel("time")
        self.axs.set_ylabel("temp[℃]")
        self.axs.grid(True)
        self.axs.legend(loc="lower left", fontsize=8) # (3)凡例表示
        await self.update_async()

    def build(self):
        return MatplotlibChart(self.fig, expand=True)