import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import flet as ft
from flet.matplotlib_chart import MatplotlibChart
import japanize_matplotlib

matplotlib.use("svg")

class tempGraph(ft.UserControl):
    def __init__(self, visible=True):
        super().__init__(self)
        #追加したプロパティ
        self.counter = 0 
        self.on_countup = lambda: None
        self.visibleBool = visible
        
        self.fig, self.axs = plt.subplots(2, 2, figsize=(8, 8)) # (1)fig, axs = plt.subplots(2, 2)で2x2のグラフを作成
        self.fig.subplots_adjust(wspace=0.3, hspace=0.3, top=0.95, bottom=0.07, right=0.98, left=0.13) # (2)グラフ間のスペースを設定
        
        # 折れ線グラフを出力
        self.x0 = np.array([])
        self.y01 = np.array([])
        self.y02 = np.array([])
        self.y03 = np.array([])
        self.y04 = np.array([])
        self.y05 = np.array([])
        self.axs[0, 0].plot(self.x0, self.y01, color="k", label="temp")
        self.axs[0, 0].plot(self.x0, self.y02, color="b", label="a0")
        self.axs[0, 0].plot(self.x0, self.y03, color="r", label="a1")
        self.axs[0, 0].plot(self.x0, self.y04, color="g", label="a2")
        self.axs[0, 0].plot(self.x0, self.y05, color="m", label="a3")
        self.axs[0, 0].set_xlabel("time")
        self.axs[0, 0].set_ylabel("temp[℃]")
        self.axs[0, 0].grid(True)
        self.axs[0, 0].legend(loc="lower left", fontsize=8) # (3)凡例表示
        
        self.axs[0, 0].set_title("Outside temperature and inside temperature")
        self.axs[0, 0].ylim = (0, 100)

        self.y06 = np.array([])
        self.y07 = np.array([])
        self.y08 = np.array([])

        self.axs[0, 1].plot(self.x0, self.y08)
        self.axs[0, 1].set_xlabel("time")
        self.axs[0, 1].set_ylabel("Altitude[m]")
        self.axs[0, 1].grid(True)
        self.axs[0, 1].set_title("Altitude")
        # self.axs[0, 1].legend(loc="lower left", fontsize=8) # (3)凡例表示
        
        self.axs[1, 0].plot(self.x0, self.y06)
        self.axs[1, 0].set_xlabel("time")
        self.axs[1, 0].set_ylabel("Pressure[hPa]")
        self.axs[1, 0].grid(True)
        self.axs[1, 0].set_title("Pressure")
        # self.axs[1, 0].legend(loc="lower left", fontsize=8) # (3)凡例表示
    
        self.axs[1, 1].plot(self.x0, self.y07)
        self.axs[1, 1].set_xlabel("time")
        self.axs[1, 1].set_ylabel("Humidity[%]")
        self.axs[1, 1].grid(True)
        self.axs[1, 1].set_title("Humidity")
        # self.axs[1, 1].legend(loc="lower left", fontsize=8) # (3)凡例表示

    async def setVisible(self, visibleb):
        self.visibleBool = visibleb
        await self.update_async()

    async def setVisibleYes(self):
        self.visibleBool = True
        self.visible = True
        await self.update_async()

    async def setVisibleNot(self):
        self.visibleBool = False
        self.visible = False
        await self.update_async()
        
    async def set(self, time, temp, pressure, humidity, altitude, a0, a1, a2, a3):
        self.axs[0, 0].cla()
        self.axs[0, 1].cla()
        self.axs[1, 0].cla()
        self.axs[1, 1].cla()
        
        self.x0 = np.array(time)
        self.y01 = np.array(temp)
        self.y02 = np.array(a0)
        self.y03 = np.array(a1)
        self.y04 = np.array(a2)
        self.y05 = np.array(a3)
        self.axs[0, 0].ylim = (0, 100)
        self.axs[0, 0].plot(self.x0, self.y01, color="k", label="temp")
        self.axs[0, 0].plot(self.x0, self.y02, color="b", label="a0")
        self.axs[0, 0].plot(self.x0, self.y03, color="r", label="a1")
        self.axs[0, 0].plot(self.x0, self.y04, color="g", label="a2")
        self.axs[0, 0].plot(self.x0, self.y05, color="m", label="a3")
        self.axs[0, 0].set_xlabel("time")
        self.axs[0, 0].set_ylabel("temp[℃]")
        self.axs[0, 0].grid(True)
        self.axs[0, 0].legend(loc="lower left", fontsize=8) # (3)凡例表示
        self.axs[0, 0].set_title("Outside temperature and inside temperature")

        self.y06 = np.array(pressure)
        self.y07 = np.array(humidity)
        self.y08 = np.array(altitude)

        self.axs[0, 1].plot(self.x0, self.y08)
        self.axs[0, 1].set_xlabel("time")
        self.axs[0, 1].set_ylabel("Altitude[m]")
        self.axs[0, 1].grid(True)
        self.axs[0, 1].set_title("Altitude")
        # self.axs[0, 1].legend(loc="lower left", fontsize=8) # (3)凡例表示
        
        self.axs[1, 0].plot(self.x0, self.y06)
        self.axs[1, 0].set_xlabel("time")
        self.axs[1, 0].set_ylabel("Pressure[hPa]")
        self.axs[1, 0].grid(True)
        self.axs[1, 0].set_title("Pressure")
        # self.axs[1, 0].legend(loc="lower left", fontsize=8) # (3)凡例表示
    
        self.axs[1, 1].plot(self.x0, self.y07)
        self.axs[1, 1].set_xlabel("time")
        self.axs[1, 1].set_ylabel("Humidity[%]")
        self.axs[1, 1].grid(True)
        self.axs[1, 1].set_title("Humidity")
        # self.axs[1, 1].legend(loc="lower left", fontsize=8) # (3)凡例表示

        await self.update_async()

    async def reset(self):
        self.axs[0, 0].cla()
        self.axs[0, 1].cla()
        self.axs[1, 0].cla()
        self.axs[1, 1].cla()
        
        # self.fig, self.axs = plt.subplots()
        self.x0 = np.array([])
        self.y01 = np.array([])
        self.y02 = np.array([])
        self.y03 = np.array([])
        self.y04 = np.array([])
        self.y05 = np.array([])
        self.axs[0, 0].plot(self.x0, self.y01, color="k", label="temp")
        self.axs[0, 0].plot(self.x0, self.y02, color="b", label="a0")
        self.axs[0, 0].plot(self.x0, self.y03, color="r", label="a1")
        self.axs[0, 0].plot(self.x0, self.y04, color="g", label="a2")
        self.axs[0, 0].plot(self.x0, self.y05, color="m", label="a3")
        self.axs[0, 0].set_xlabel("time")
        self.axs[0, 0].set_ylabel("temp[℃]")
        self.axs[0, 0].grid(True)
        self.axs[0, 0].legend(loc="lower left", fontsize=8) # (3)凡例表示

        self.axs[0, 0].set_title("Outside temperature and inside temperature")
        self.axs[0, 0].ylim = (0, 100)

        self.y06 = np.array([])
        self.y07 = np.array([])
        self.y08 = np.array([])

        self.axs[0, 1].plot(self.x0, self.y08)
        self.axs[0, 1].set_xlabel("time")
        self.axs[0, 1].set_ylabel("Altitude[m]")
        self.axs[0, 1].grid(True)
        self.axs[0, 1].set_title("Altitude")
        # self.axs[0, 1].legend(loc="lower left", fontsize=8) # (3)凡例表示
        
        self.axs[1, 0].plot(self.x0, self.y06)
        self.axs[1, 0].set_xlabel("time")
        self.axs[1, 0].set_ylabel("Pressure[hPa]")
        self.axs[1, 0].grid(True)
        self.axs[1, 0].set_title("Pressure")
        # self.axs[1, 0].legend(loc="lower left", fontsize=8) # (3)凡例表示
    
        self.axs[1, 1].plot(self.x0, self.y07)
        self.axs[1, 1].set_xlabel("time")
        self.axs[1, 1].set_ylabel("Humidity[%]")
        self.axs[1, 1].grid(True)
        self.axs[1, 1].set_title("Humidity")
        # self.axs[1, 1].legend(loc="lower left", fontsize=8) # (3)凡例表示

        await self.update_async()

    def build(self):
        return MatplotlibChart(self.fig, expand=True, visible=self.visibleBool)