import os
import flet as ft
from flet import AppBar, ElevatedButton, Page, Text, View, colors, TextField
import asyncio
import numpy as np
import matplotlib.pyplot as plt
import requests
import time
import pyperclip
from tempgraph import tempGraph
from stopwatch import StopwatchApp
import copy
import re
import datetime

dt_now = datetime.datetime.now()

os.environ["FLET_WS_MAX_MESSAGE_SIZE"] = "8000000"

async def main(page: Page):
    time=[]
    temp=[]
    pressure=[]
    humidity=[]
    altitude=[]
    a0=[]
    a1=[]
    a2=[]
    a3=[]
    
    r_time=[]
    r_temp=[]
    r_pressure=[]
    r_humidity=[]
    r_altitude=[]
    r_a0=[]
    r_a1=[]
    r_a2=[]
    r_a3=[]
    
    # ストレージ
    # await page.client_storage.clear_async()
    global recordStopWatchSystem
    recordStopWatchSystem=StopwatchApp()
    global recordStartTime, recordStatus, recordDataStatus, recordStartAltitude
    recordStartTime=-1.0
    recordStartAltitude=0.0
    recordStatus=False
    recordDataStatus=False

    ################################
    ### Snackbar
    ################################
    
    page.snack_bar = ft.SnackBar(
        content=ft.Text("Hello, world!"),
        action="Alright!",
    )

    async def openSnackbar(text):
        page.snack_bar = ft.SnackBar(ft.Text(text))
        page.snack_bar.open = True
        await page.update_async()

    ###################
    ## Folder Pickup System
    ###################
    
    # Open directory dialog
    async def get_directory_result(e: ft.FilePickerResultEvent):
        directory_path = e.path if e.path else ""
        await page.client_storage.set_async("directory_path", directory_path)
        projectDirectory.value="保存先: "+directory_path
        await openSnackbar("測定データの保存ディレクトリを設定しました: "+directory_path)
        await projectDirectory.update_async()

    get_directory_dialog = ft.FilePicker(on_result=get_directory_result)
    
    page.overlay.append(get_directory_dialog)


    global rawResponseData, recordRawData
    rawResponseData=""
    recordRawData=""

    global connectStatus
    connectStatus = False

    ###################
    ## 機材管理 System
    ###################
    
    def find_option(option_name):
        for option in baloonSelecter.options:
            if option_name == option.key:
                return option
        return None
        
    async def dropdown_changed(e):
        if await page.client_storage.contains_key_async("hontai_ip") == False or await page.client_storage.get_async("hontai_ip")==None:
            await openSnackbar("接続先が未設定です。")
            baloonSelecter.value=None
            await page.update_async()
            await reloadBaloons(e)
            return()
        if await page.client_storage.contains_key_async("directory_path") == False or await page.client_storage.get_async("directory_path")=="":
            await openSnackbar("ディレクトリが指定されていません。保存先を設定してください。")
            baloonSelecter.value=None
            await page.update_async()
            await reloadBaloons(e)
            return()
        if os.path.isdir(await page.client_storage.get_async("directory_path")+"/"+baloonSelecter.value) == False:
            await openSnackbar("ディレクトリが存在しません。")
            baloonSelecter.value=None
            await page.update_async()
            await reloadBaloons(e)
            return()
        projectTitle.value = f"プロジェクト名: {baloonSelecter.value}"
        if connectStatus==True and ((recordStatus==False and recordDataStatus==True) or recordDataStatus==False):
            recordStartButton.disabled=False
            await recordStartButton.update_async()
        await page.update_async()
        await page.client_storage.set_async("baloon", baloonSelecter.value)

    async def add_clicked(e):
        if not option_textbox.value:
            option_textbox.error_text = "入力してください。"
            await page.update_async()
            return()
        option_textbox.error_text = ""
        if await page.client_storage.contains_key_async("directory_path") == False or await page.client_storage.get_async("directory_path")=="":
            page.banner.content=ft.Column(spacing=0, controls=[ft.Text("データの保存先が未指定です。", theme_style=ft.TextThemeStyle.TITLE_LARGE), ft.Text("ファイル＞ディレクトリを選択 から、測定したデータの保存先を指定してください。")])
            page.banner.open = True
            await page.update_async()
            return()
        newBaloonName=re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', option_textbox.value)
        try:
            os.mkdir(await page.client_storage.get_async("directory_path")+"/"+newBaloonName)
        except FileExistsError as e:
            print("FileExistsError")
            await openSnackbar("既にディレクトリが存在します。別の名前を指定してください。")
        except FileNotFoundError as e:
            await openSnackbar("ディレクトリが存在しません。再度保存先を設定してください。")
        except Exception as e:
            await openSnackbar("予期しないエラーが発生しました: "+str(e))
        else:
            baloonSelecter.options.append(ft.dropdown.Option(newBaloonName))
            baloonSelecter.value = newBaloonName
            await openSnackbar("フォルダを作成しました: "+newBaloonName)
            option_textbox.value = ""
            await baloonSelecter.update_async()
            await page.update_async()

    async def delete_clicked(e):
        option = find_option(baloonSelecter.value)
        if option != None:
            baloonSelecter.options.remove(option)
            # d.value = None
            await page.update_async()
    baloonSelecter = ft.Dropdown(label="使用機材", width=200,hint_text="機材管理タブで追加可能", prefix_icon=ft.icons.AIRPLANEMODE_ACTIVE_ROUNDED, on_change=dropdown_changed)

    async def reloadBaloons(e):
        if await page.client_storage.contains_key_async("directory_path") == True or await page.client_storage.get_async("directory_path")!="":
            dir_path=await page.client_storage.get_async("directory_path")
            files_dir = [
                ft.dropdown.Option(f) for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))
            ]
            baloonSelecter.options=files_dir
            await baloonSelecter.update_async()
        else:
            await openSnackbar("ディレクトリが指定されていません。保存先を設定してください。")
            

    if await page.client_storage.contains_key_async("directory_path") == True or await page.client_storage.get_async("directory_path")!="":
        dir_path=await page.client_storage.get_async("directory_path")
        try:
            files_dir = [
                ft.dropdown.Option(f) for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))
            ]
        except FileNotFoundError as e:
            await openSnackbar("ディレクトリが存在しません。再指定してください。: "+str(e))
            await page.client_storage.set_async("directory_path", "")
        except Exception as e:
            await openSnackbar("エラーが発生しました。ディレクトリを再指定してください。: "+str(e))
            await page.client_storage.set_async("directory_path", "")
        else:
            baloonSelecter.options=files_dir
        await page.update_async()
    # else:
    #     baloonSelecter.error_text="機材管理タブから追加してください。"
    #     await page.update_async()
    
    option_textbox = ft.TextField(hint_text="新しいバルーンの名前を決めてください。", label="新しいバルーン名")
    add = ft.ElevatedButton("追加", on_click=add_clicked)
    delete = ft.OutlinedButton("Delete selected", on_click=delete_clicked)
    
    async def view_hontai_ip():
        if await page.client_storage.contains_key_async("hontai_ip") == False:
            return("未設定")
        elif await page.client_storage.get_async("hontai_ip")=="":
            return("未設定")
        else:
            return(await page.client_storage.get_async("hontai_ip"))
        
    async def view_hontai_port():
        if await page.client_storage.contains_key_async("hontai_port") == False:
            return("未設定")
        elif await page.client_storage.get_async("hontai_port")=="":
            return("未設定")
        else:
            return(await page.client_storage.get_async("hontai_port"))
        
    async def close_banner(e):
        page.banner.open = False
        await page.update_async()
    global bannerContents
    bannerContents=ft.Text("")

    global isRecordStop
    isRecordStop=True
    


    table=ft.DataTable(
        heading_row_height=0,
        # border=ft.border.all(2, "red"),
        show_bottom_border=True,
        #columns 里必须添加 DataColumn 类型的控件
        #data_row_max_height=33,
        horizontal_margin=0,
        columns=[
                ft.DataColumn(ft.Text("時間[sec]"), numeric=True),
                ft.DataColumn(ft.Text("外気温度[℃]"), numeric=True),
                ft.DataColumn(ft.Text("圧力[hPa]"), numeric=True),
                ft.DataColumn(ft.Text("湿度[%]"), numeric=True),
                ft.DataColumn(ft.Text("標高[m]"), numeric=True),
                ft.DataColumn(ft.Text("a0[℃]"), numeric=True),
                ft.DataColumn(ft.Text("a1[℃]"), numeric=True),
                ft.DataColumn(ft.Text("a2[℃]"), numeric=True),
                ft.DataColumn(ft.Text("a3[℃]"), numeric=True),
            ],
        #rows 里必须添加 DataRow 类型的控件
        #DataRow 
        )
    
    realtimeRecordTable=ft.DataTable(
        heading_row_height=0,
        # border=ft.border.all(2, "red"),
        show_bottom_border=True,
        #columns 里必须添加 DataColumn 类型的控件
        #data_row_max_height=33,
        horizontal_margin=0,
        columns=[
                ft.DataColumn(ft.Text("時間[sec]"), numeric=True),
                ft.DataColumn(ft.Text("外気温度[℃]"), numeric=True),
                ft.DataColumn(ft.Text("圧力[hPa]"), numeric=True),
                ft.DataColumn(ft.Text("湿度[%]"), numeric=True),
                ft.DataColumn(ft.Text("標高[m]"), numeric=True),
                ft.DataColumn(ft.Text("a0[℃]"), numeric=True),
                ft.DataColumn(ft.Text("a1[℃]"), numeric=True),
                ft.DataColumn(ft.Text("a2[℃]"), numeric=True),
                ft.DataColumn(ft.Text("a3[℃]"), numeric=True),
            ],
        #rows 里必须添加 DataRow 类型的控件
        #DataRow 
        )
    async def addRealtimeData(resList, resListFloat):
        global rawResponseData
        b=ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(resList[0], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[0])),
                    ft.DataCell(ft.Text(resList[1], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[1])),
                    ft.DataCell(ft.Text(resList[2], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[2])),
                    ft.DataCell(ft.Text(resList[3], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[3])),
                    ft.DataCell(ft.Text(resList[4], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[4])),
                    ft.DataCell(ft.Text(resList[5], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[5])),
                    ft.DataCell(ft.Text(resList[6], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[6])),
                    ft.DataCell(ft.Text(resList[7], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[7])),
                    ft.DataCell(ft.Text(resList[8], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(resList[8])),
                    ])
        realtimeRecordTable.rows.insert(0, b)
        realtimeRecordTable.rows=realtimeRecordTable.rows[:10]
        for i in range(0, 9):
            realtimeData[i].value=resList[i]
            # rtNowData[i].on_click=lambda e: pyperclip.copy(resList[i])
        global recordStartTime, recordStartAltitude, recordStatus, recordDataStatus, recordRawData, recordDateTime, recordBaloonName, isRecordStop
        if isRecordStop==False:
            if recordStartTime==-1.00:
                recordStartTime=resListFloat[0]
                recordStartAltitude=resListFloat[4]
                recordRawData+="time[sec], temperature[degC], pressure[hPa], humidity[%], altitude[m], a0, a1, a2, a3\n"
                recordBaloonName=baloonSelecter.value
                recordDateTime=copy.deepcopy(dt_now.strftime('%Y-%m-%d_%H-%M-%S'))
            recordDataStatus = True
            recordList=copy.deepcopy(resList)
            recordList[0]='{:.2f}'.format(resListFloat[0]-recordStartTime)
            recordList[4]='{:.1f}'.format(resListFloat[4]-recordStartAltitude)
            recordListFloat=copy.deepcopy(resListFloat)
            recordListFloat[0]=round(resListFloat[0]-recordStartTime,2)
            recordListFloat[4]=round(resListFloat[4]-recordStartAltitude,1)
            b=ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(recordList[0], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[0])),
                        ft.DataCell(ft.Text(recordList[1], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[1])),
                        ft.DataCell(ft.Text(recordList[2], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[2])),
                        ft.DataCell(ft.Text(recordList[3], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[3])),
                        ft.DataCell(ft.Text(recordList[4], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[4])),
                        ft.DataCell(ft.Text(recordList[5], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[5])),
                        ft.DataCell(ft.Text(recordList[6], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[6])),
                        ft.DataCell(ft.Text(recordList[7], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[7])),
                        ft.DataCell(ft.Text(recordList[8], selectable=True, max_lines=1, no_wrap=True, size=16), on_tap=lambda e: pyperclip.copy(recordList[8])),
                        ])
            # table.rows.append(b) kx
            r_time.append(recordListFloat[0])
            r_temp.append(recordListFloat[1])
            r_pressure.append(recordListFloat[2])
            r_humidity.append(recordListFloat[3])
            r_altitude.append(recordListFloat[4])
            r_a0.append(recordListFloat[5])
            r_a1.append(recordListFloat[6])
            r_a2.append(recordListFloat[7])
            r_a3.append(recordListFloat[8])
            recordRawData+=', '.join(recordList)+"\n"
            rawRecorddata_tx.value=recordRawData

            for i in range(0, 9):
                rtNowData[i].value=recordList[i]
            await table_column.update_async()
            await rawRecorddata_tx.update_async()
            # await table.update_async() kx
        await realtimeTable.update_async()
        await realtimeRecordTable.update_async()

        await page.update_async()
        # rtNowData[0].value=resList[0]
        # rtNowData[0].on_click=lambda e: pyperclip.copy(resList[0])
        time.append(resListFloat[0])
        temp.append(resListFloat[1])
        pressure.append(resListFloat[2])
        humidity.append(resListFloat[3])
        altitude.append(resListFloat[4])
        a0.append(resListFloat[5])
        a1.append(resListFloat[6])
        a2.append(resListFloat[7])
        a3.append(resListFloat[8])
        await realtimeGraphSystem.set(time=time[-100:], temp=temp[-100:], pressure=pressure[-100:], humidity=humidity[-100:], altitude=altitude[-100:], a0=a0[-100:], a1=a1[-100:], a2=a2[-100:], a3=a3[-100:])

        # if recordStatus:
        #     await tempGraphSystem.set(time=r_time, temp=r_temp, pressure=r_pressure, humidity=r_humidity, altitude=r_altitude, a0=r_a0, a1=r_a1, a2=r_a2, a3=r_a3)

        await page.update_async()
        
        #print(resList)
        

    global recordDateTime
    recordDateTime=""
    recordBaloonName=""

    async def addRecordData(resList, resListFloat):
        return()


    async def event_listener(response):
        global rawResponseData
        # Your existing implementation for handling server response
        # This function is already prepared, so no need to implement it here

        if response.startswith('time'):
            await openSnackbar("遠隔データ測定キットに接続しました。データを受信しています。")
            rawResponseData+=response[:85]+"\n"
            rawdata_tx.value=rawResponseData
            await rawdata_tx.update_async()
            if (baloonSelecter.value != None and baloonSelecter.value != "") and ((recordStatus==False and recordDataStatus==True) or recordDataStatus==False):
                recordStartButton.disabled=False
                await recordStartButton.update_async()
                #print(resList)
                #resList
                #print(f"Received response: {response}")
            # print("Connected.")
            page.window_resizable=False
            await page.update_async()
            return()
        else:
            rawResponseData+=response+"\n"
            rawdata_tx.value=rawResponseData
            await rawdata_tx.update_async()
            try:
                resList=[x.strip() for x in response.split(',')]
                resListFloat=[float(x.strip()) for x in response.split(',')]
            except Exception as e:
                await openSnackbar("エラーが発生しました。不適切なデータを受信した可能性があります。: "+str(e))
                print(e)
            else:
                await addRecordData(resList, resListFloat)
                await addRealtimeData(resList, resListFloat)
                #print(resList)
                #resList
                #print(f"Received response: {response}")

    # setuzokuStatusView=ft.SubmenuButton(
    #             content=ft.Image(
    #                                     src=f"connecting.gif",
    #                                     # width=100,
    #                                     height=40,
    #                                     fit=ft.ImageFit.FIT_HEIGHT,
    #                                 ),
    #             visible=False
    #         )
    async def connectPC(e):
        # await countupTimer.reset(seconds=0)
        if await page.client_storage.contains_key_async("directory_path") == False or await page.client_storage.get_async("directory_path")=="":
            page.banner.content=ft.Column(spacing=0, controls=[ft.Text("データの保存先が未指定です。", theme_style=ft.TextThemeStyle.TITLE_LARGE), ft.Text("ファイル＞ディレクトリを選択 から、測定したデータの保存先を指定してください。")])
            page.banner.open = True
            await page.update_async()
            return()
        await close_banner(e)
        global connectStatus
        global recordStatus, isRecordStop
        connectStatus=True
        setuzokuStartButton.text="接続中..."
        setuzokusaki.disabled=True
        setuzokuStartButton.disabled=True
        setuzokuStopButton.disabled=False
        time.clear()
        temp.clear()
        pressure.clear()
        humidity.clear()
        altitude.clear()
        a0.clear()
        a1.clear()
        a2.clear()
        a3.clear()
        await realtimeGraphSystem.reset()
        await setuzokuStartButton.update_async()
        await setuzokusaki.update_async()
        page.splash = ft.ProgressBar()
        await page.update_async()

        try:
            server_url = await view_hontai_ip()
            response = requests.get(server_url, stream=True)
            response.raise_for_status()
            print("\nConnected to server: "+server_url+"\n")
            page.splash = None
            client = response.iter_lines(chunk_size=1, decode_unicode=True)
            # await countupTimer.start()
            for line in client:
                if connectStatus==False:
                    # await setuzokuStatusView.update_async()
                    break
                if recordStatus==False:
                    isRecordStop=True
                else:
                    isRecordStop=False
                if not line:
                    continue
                print(line)
                await event_listener(line)

                # if line.startswith('data:'):
                #     data = line[6:]
                #     event_listener(data)
        except requests.exceptions.RequestException as e:
            global bannerContents
            bannerContents.value=f"エラー内容: {e}"
            page.banner.content = ft.Column(spacing=0, controls=[ft.Text("測定キットとの接続に失敗しました。", theme_style=ft.TextThemeStyle.TITLE_LARGE), bannerContents])
            page.banner.open = True
            await page.update_async()
            await disconnectPC(e)
            print(f"Error connecting to the server: {e}")
        else:
            setuzokusaki.disabled=False
            setuzokuStartButton.disabled=False
            setuzokuStopButton.disabled=True
            # setuzokuStatusView.visible=True
            await menubaritem.update_async()
            await menubar.update_async()
            await page.update_async()
            await openSnackbar("遠隔データ測定キットとの接続を終了しました。")

    page.banner = ft.Banner(
        # bgcolor=ft.colors.AMBER_100,
        leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
        content=ft.Column(spacing=0, controls=[ft.Text("測定キットとの接続に失敗しました。", theme_style=ft.TextThemeStyle.TITLE_LARGE), bannerContents]),
        actions=[
            ft.TextButton("再試行", on_click=connectPC),
            ft.TextButton("閉じる", on_click=close_banner),
        ],
    )
    
    async def disconnectPC(e):
        await recordStop(e)
        global connectStatus
        connectStatus = False
        setuzokuStopButton.disabled=True
        await setuzokuStopButton.update_async()
        setuzokuStartButton.text="接続開始"
        setuzokusaki.disabled=False
        setuzokuStartButton.disabled=False
        recordStartButton.disabled=True
        await recordStartButton.update_async()
        # await countupTimer.stop()
        page.window_resizable=True
        page.splash = None
        await page.update_async()
        
    class Countdown(ft.UserControl):
        def __init__(self, seconds):
            super().__init__()
            self.seconds = seconds

        async def did_mount_async(self):
            self.running = True
            asyncio.create_task(self.update_timer())

        async def will_unmount_async(self):
            self.running = False

        async def update_timer(self):
            while self.seconds and self.running:
                # mins, secs = divmod(self.seconds, 60)
                self.countdown.value = "{:.1f}".format(self.seconds)
                await button_clicked( "{:.1f}".format(self.seconds))
                self.seconds -= 0.5
                await self.update_async()
                await asyncio.sleep(0.5)
        def build(self):
            self.countdown = ft.Text()
            return self.countdown
        
    # class Countup(ft.UserControl):
    #     def __init__(self, seconds):
    #         super().__init__()
    #         self.seconds = seconds

    #     async def reset(self, seconds):
    #         self.seconds = seconds

    #     async def did_mount_async(self):
    #         self.running = False
    #         asyncio.create_task(self.update_timer())
    #         mins, secs = divmod(self.seconds, 60)
    #         self.countup.value = "{:02d}:{:02d}".format(mins, secs)
    #         await self.update_async()
                    
    #     async def start(self):
    #         self.running = True
    #         asyncio.create_task(self.update_timer())

    #     async def will_unmount_async(self):
    #         self.running = False
            

    #     async def stop(self):
    #         self.running = False

    #     async def update_timer(self):
    #         while self.running:
    #             mins, secs = divmod(self.seconds, 60)
    #             self.countup.value = "{:02d}:{:02d}".format(mins, secs)
    #             self.seconds += 1
    #             await self.update_async()
    #             await asyncio.sleep(1)

    #     def build(self):
    #         self.countup = ft.Text()
    #         return self.countup

    ################################
    ### Page System
    ################################
    
    page.title = "EBDAS - Ehime Baloon Data Analyze System"
    body=[]
    bodySide=[]
    rtTab=[]
    rtTabSide=[]

    # print("Initial route:", page.route)

    async def open_settings(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        await page.update_async()

    async def close_resetAlert(e):
        resetAlert.open = False
        await page.update_async()
        
    async def rtReset(e):
        global recordStartTime, recordStatus, recordStartAltitude
        if recordStatus:
            await openSnackbar("記録中のため、リセットできません。")
            return()
        global recordStopWatchSystem
        recordTime=recordStopWatchSystem.stop()
        recordStopWatchSystem.reset()
        recordTimeView.value="-"
        await recordTimeView.update_async()
        global rawResponseData, recordRawData, recordDataStatus
        realtimeRecordTable.rows.clear()
        # table.rows.clear() kx
        time.clear()
        temp.clear()
        pressure.clear()
        humidity.clear()
        altitude.clear()
        a0.clear()
        a1.clear()
        a2.clear()
        a3.clear()
        r_time.clear()
        r_temp.clear()
        r_pressure.clear()
        r_humidity.clear()
        r_altitude.clear()
        r_a0.clear()
        r_a1.clear()
        r_a2.clear()
        r_a3.clear()
        for i in range(0, 9):
            rtNowData[i].value="-"
            realtimeData[i].value="-"
            rtNowData[i].on_click=lambda e: pyperclip.copy("-")
        rawResponseData=""
        recordRawData=""
        rawdata_tx.value=""
        rawRecorddata_tx.value=""
        recordDeleteTitle.color=None
        recordDeleteText.color=None
        recordDeleteIcon.color=None
        recordStartTime=-1.0
        recordStartAltitude=0.0
        recordStatus=False
        recordDataStatus=False
        baloonSelecter.value=None
        recordStartButton.disabled=True
        recordSaveButton.disabled=True
        recordDeleteButton.disabled=True
        await tempGraphSystem.reset()
        await realtimeGraphSystem.reset()
        await close_resetAlert(e)
        # await table.update_async() kx
        await rawRecorddata_tx.update_async()
        await table_column.update_async()
        await realtimeTable.update_async()
        await realtimeRecordTable.update_async()
        await baloonSelecter.update_async()
        await recordStartButton.update_async()
        await recordSaveButton.update_async()
        await recordDeleteButton.update_async()
        await page.update_async()

    resetAlert = ft.AlertDialog(
        modal=True,
        title=ft.Text("これまでのデータを削除しますか?"),
        content=ft.Text("測定キットから送られてきたデータを全て削除します。"),
        actions=[
            ft.TextButton("削除する", on_click=rtReset),
            ft.TextButton("削除しない", on_click=close_resetAlert),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        # on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    async def open_resetAlert(e):
        global recordStartTime, recordStatus
        if recordStatus:
            await openSnackbar("記録中のため、リセットできません。")
            return()
        page.dialog = resetAlert
        resetAlert.open = True
        await page.update_async()

    
    if await view_hontai_ip()=="未設定":
        setuzokusaki=ElevatedButton(f"接続先: 未設定です。クリックして設定してください。", on_click=open_settings, disabled=connectStatus)
        setuzokuStartButton=ElevatedButton(f"接続開始", on_click=connectPC, disabled=True)
    else:
        setuzokusaki=ElevatedButton(f"接続先: {await view_hontai_ip()}", on_click=open_settings, disabled=connectStatus)
        setuzokuStartButton=ElevatedButton(f"接続開始", on_click=connectPC, disabled=connectStatus)
        
    async def rtAutoScChange(e):
        if rtAutoScSwitch.value:
            lv.auto_scroll=False
        else:
            lv.auto_scroll=True
        await lv.update_async()
        
    rtAutoScSwitch=ft.Switch(label="自動スクロール(OFF推奨)", on_change=rtAutoScChange, value=False)
    
    setuzokuStopButton=ElevatedButton(f"接続終了", on_click=disconnectPC, disabled=True)
    rtResetButton=ft.ElevatedButton(text="リセット", on_click=open_resetAlert, data=0)
    # countupTimer=Countup(0)
    await page.add_async(
        AppBar(
                        title=ft.Row(
                                spacing=5,
                                controls=[
                                    # Text("EBDAS"),
                                    ft.Image(
                                        src=f"ebdas.png",
                                        # width=100,
                                        height=50,
                                        fit=ft.ImageFit.FIT_HEIGHT,
                                    ),
                                    setuzokusaki,
                                    setuzokuStartButton,
                                    setuzokuStopButton,
                                    rtResetButton,

                                    # ft.Text("接続時間:"),
                                    
                                ],
                            ),
                        actions=[
                            
                        ]
                    )
    )
    
    async def close_dlg(e):
        dlg_modal.open = False
        await page.update_async()
    async def save_settings(e):
        if not txt_hontai_ip.value:
            txt_hontai_ip.error_text = "入力してください。"
            await page.update_async()
            return()
        else:
            txt_hontai_ip.error_text = ""
        # if not txt_hontai_port.value:
        #     txt_hontai_port.error_text = "入力してください。"
        #     await page.update_async()
        #     return()
        # else:
        #     txt_hontai_port.error_text = ""
        await page.client_storage.set_async("hontai_ip", txt_hontai_ip.value)
        # await page.client_storage.set_async("hontai_port", txt_hontai_port.value)
        setuzokusaki.text=f"接続先: {txt_hontai_ip.value}"
        setuzokusaki.disabled=False
        setuzokuStartButton.disabled=False
        await openSnackbar("設定を保存しました。")
        await close_dlg(e)
        await page.update_async()


    txt_hontai_ip = TextField(label="測定キット本体のアドレス", value=await page.client_storage.get_async("hontai_ip"), hint_text="http://KIT38Mikan.local:80")
    # txt_hontai_port = TextField(label="測定キット本体のポート番号", value=await page.client_storage.get_async("hontai_port"))
    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("設定"),
        content=txt_hontai_ip,
        actions=[
            ft.TextButton("保存", on_click=save_settings),
            ft.TextButton("キャンセル", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        #on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )
    
    rtNowData=[
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
    ]
    
    realtimeData=[
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
        ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18),
    ]
    projectTitle = ft.Text("プロジェクト: -")
    projectDirectory = ft.Text("保存先: -" if await page.client_storage.contains_key_async("directory_path") == False or await page.client_storage.get_async("directory_path")=="" else "保存先: "+ await page.client_storage.get_async("directory_path"))
    projectFlyCount = ft.Text("飛行回数: -")


    if await page.client_storage.contains_key_async("baloon") == True and await page.client_storage.get_async("baloon")!=None:
        if await page.client_storage.contains_key_async("hontai_ip") == False or await page.client_storage.get_async("hontai_ip")==None:
            await openSnackbar("接続先が未設定です。")
            await page.client_storage.remove_async("baloon")
            await page.update_async()
            return()
        if await page.client_storage.contains_key_async("directory_path") == False or await page.client_storage.get_async("directory_path")=="":
            await openSnackbar("ディレクトリが指定されていません。保存先を設定してください。")
            await page.client_storage.remove_async("baloon")
            await page.update_async()
            return()
        if os.path.isdir(await page.client_storage.get_async("directory_path")+"/"+await page.client_storage.get_async("baloon")) == False:
            await openSnackbar("ディレクトリが存在しません。")
            await page.client_storage.remove_async("baloon")
            await page.update_async()
            return()
        baloonSelecter.value=await page.client_storage.get_async("baloon")
        projectTitle.value = f"プロジェクト名: {baloonSelecter.value}"
        if connectStatus==True and ((recordStatus==False and recordDataStatus==True) or recordDataStatus==False):
            recordStartButton.disabled=False
            await recordStartButton.update_async()
        await page.update_async()


    async def openFilePicker(e):
        await get_directory_dialog.get_directory_path_async(dialog_title="測定したデータを保存するディレクトリを選択してください。")
    
    recordTimeView = ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    
    menubar = ft.MenuBar(
        expand=True,
        style=ft.MenuStyle(
            alignment=ft.alignment.top_left,
            mouse_cursor={
                ft.MaterialState.HOVERED: ft.MouseCursor.WAIT,
                ft.MaterialState.DEFAULT: ft.MouseCursor.ZOOM_OUT,
            },
        ),
        controls=[
            ft.SubmenuButton(
                content=ft.Text("ファイル"),
                # on_open=handle_on_open,
                # on_close=handle_on_close,
                # on_hover=handle_on_hover,
                controls=[
                    ft.SubmenuButton(
                        content=ft.Text("情報"),
                        leading=ft.Icon(ft.icons.INFO),
                        controls=[
                            ft.MenuItemButton(
                                content=projectTitle
                            ),
                            ft.MenuItemButton(
                                content=projectDirectory,
                                # on_click=get_directory_dialog.get_directory_path_async,
                                # disabled=page.web,
                            ),
                            ft.MenuItemButton(
                                content=projectFlyCount
                            ),
                        ]
                        # on_click=handle_menu_item_click
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("ディレクトリを選択"),
                        leading=ft.Icon(ft.icons.SAVE),
                        on_click=openFilePicker,
                        disabled=page.web,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("閉じる"),
                        leading=ft.Icon(ft.icons.CLOSE),
                        style=ft.ButtonStyle(
                            bgcolor={ft.MaterialState.HOVERED: ft.colors.RED_300}
                        ),
                        # on_click=handle_menu_item_click
                    ),
                ],
            ),
            ft.SubmenuButton(
                content=ft.Text("編集"),
                # on_open=handle_on_open,
                # on_close=handle_on_close,
                # on_hover=handle_on_hover,
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("測定キット接続設定"),
                        leading=ft.Icon(name="settings"),
                        on_click=open_settings
                    ),
                ],
            ),
            ft.SubmenuButton(
                content=ft.Text("表示"),
                # on_open=handle_on_open,
                # on_close=handle_on_close,
                # on_hover=handle_on_hover,
                controls=[
                    ft.SubmenuButton(
                        content=ft.Text("拡大/縮小"),
                        controls=[
                            ft.MenuItemButton(
                                content=ft.Text("Magnify"),
                                leading=ft.Icon(ft.icons.ZOOM_IN),
                                close_on_click=False,
                                style=ft.ButtonStyle(
                                    bgcolor={
                                        ft.MaterialState.HOVERED: ft.colors.PURPLE_200
                                    }
                                ),
                                # on_click=handle_menu_item_click
                            ),
                            ft.MenuItemButton(
                                content=ft.Text("Minify"),
                                leading=ft.Icon(ft.icons.ZOOM_OUT),
                                close_on_click=False,
                                style=ft.ButtonStyle(
                                    bgcolor={
                                        ft.MaterialState.HOVERED: ft.colors.PURPLE_200
                                    }
                                ),
                                # on_click=handle_menu_item_click
                            ),
                        ],
                    )
                ],
            ),
            # setuzokuStatusView,
            ft.SubmenuButton(
                content=ft.Row([ft.Text("接続時間:"), realtimeData[0]], )
            ),
            ft.SubmenuButton(
                content=ft.Row([ft.Text("測定時間:"), rtNowData[0]], )
                # on_open=handle_on_open,
                # on_close=handle_on_close,
                # on_hover=handle_on_hover,
                # controls=[
                #     ft.SubmenuButton(
                #         content=ft.Text("拡大/縮小"),
                #         controls=[
                #             ft.MenuItemButton(
                #                 content=ft.Text("Magnify"),
                #                 leading=ft.Icon(ft.icons.ZOOM_IN),
                #                 close_on_click=False,
                #                 style=ft.ButtonStyle(
                #                     bgcolor={
                #                         ft.MaterialState.HOVERED: ft.colors.PURPLE_200
                #                     }
                #                 ),
                #                 # on_click=handle_menu_item_click
                #             ),
                #             ft.MenuItemButton(
                #                 content=ft.Text("Minify"),
                #                 leading=ft.Icon(ft.icons.ZOOM_OUT),
                #                 close_on_click=False,
                #                 style=ft.ButtonStyle(
                #                     bgcolor={
                #                         ft.MaterialState.HOVERED: ft.colors.PURPLE_200
                #                     }
                #                 ),
                #                 # on_click=handle_menu_item_click
                #             ),
                #         ],
                #     )
                # ],
            ),
            ft.SubmenuButton(
                content=ft.Row([ft.Text("記録時間 :"), recordTimeView], )
            ),
        ],
    )

    
    def graphview():
        x = np.linspace(0,3,20) # 0～3まで20刻みでxの値を生成
        y = x**2 + 1            # 曲線の式(2次関数)
        plt.plot(x,y,"r-")      # 曲線を引く
        plt.show()              # グラフ表示
    
    def resultdata():
        datatable = ft.DataTable(
            width=700,
            #bgcolor="yellow",
            #border=ft.border.all(2, "red"),
            border_radius=10,
            #vertical_lines=ft.border.BorderSide(3, "blue"),
            #horizontal_lines=ft.border.BorderSide(1, "green"),
            #sort_column_index=0,
            #sort_ascending=True,
            #heading_row_color=ft.colors.BLACK12,
            heading_row_height=40,
            data_row_color={"hovered": "0x30FF0000"},
            #show_checkbox_column=True,
            divider_thickness=0,
            column_spacing=100,
            columns=[
                ft.DataColumn(
                    ft.Text("time"),
                    on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"),
                ),
                ft.DataColumn(
                    ft.Text("温度"),
                    tooltip="本体で測定した温度",
                    numeric=True,
                    on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"),
                ),
                ft.DataColumn(
                    ft.Text("湿度"),
                    tooltip="本体で測定した湿度",
                    numeric=True,
                    on_sort=lambda e: print(f"{e.column_index}, {e.ascending}"),
                ),
            ],
            # rows=[
            #     ft.DataRow(
            #         [ft.DataCell(ft.Text("A")), ft.DataCell(ft.Text("1")), ft.DataCell(ft.Text("1"))],
            #         selected=True,
            #         on_select_changed=lambda e:graphview(),
            #     ),
            #     ft.DataRow([ft.DataCell(ft.Text("B")), ft.DataCell(ft.Text("2")), ft.DataCell(ft.Text("1"))]),
            # ],
        )
        return(datatable)
    lv0 = ft.ListView(spacing=10, padding=ft.padding.only(left=20, top=10, right=20, bottom=0),)
    realtimeLv = ft.ListView(spacing=10, padding=ft.padding.only(left=20, top=10, right=20, bottom=0),)

    
    menubaritem = ft.Row([menubar])
    

    # rtNowData0=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData1=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData2=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData3=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData4=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData5=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData6=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData7=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)
    # rtNowData8=ft.Text("-", selectable=True, max_lines=1, no_wrap=True, weight=ft.FontWeight.BOLD, size=18)

    table_column=ft.DataTable(
        # border=ft.border.all(2, "red"),
        show_bottom_border=True,
        horizontal_margin=0, 
        #columns 里必须添加 DataColumn 类型的控件
        columns=[
            ft.DataColumn(ft.Text("時間[sec]"), numeric=True),
            ft.DataColumn(ft.Text("外気温度[℃]"), numeric=True),
            ft.DataColumn(ft.Text("圧力[hPa]"), numeric=True),
            ft.DataColumn(ft.Text("湿度[%]"), numeric=True),
            ft.DataColumn(ft.Text("標高[m]"), numeric=True),
            ft.DataColumn(ft.Text("a0[℃]"), numeric=True),
            ft.DataColumn(ft.Text("a1[℃]"), numeric=True),
            ft.DataColumn(ft.Text("a2[℃]"), numeric=True),
            ft.DataColumn(ft.Text("a3[℃]"), numeric=True),
        ],
        rows=[
                ft.DataRow([
                    ft.DataCell(rtNowData[0]),
                    ft.DataCell(rtNowData[1]),
                    ft.DataCell(rtNowData[2]),
                    ft.DataCell(rtNowData[3]),
                    ft.DataCell(rtNowData[4]),
                    ft.DataCell(rtNowData[5]),
                    ft.DataCell(rtNowData[6]),
                    ft.DataCell(rtNowData[7]),
                    ft.DataCell(rtNowData[8]),
                ]),
            ],
        )
        
    async def recordSave(e):
        global connectStatus, recordStatus, recordDataStatus, recordRawData, recordBaloonName, recordDateTime
        if recordStatus == True or recordDataStatus == False:
            await openSnackbar("記録データがありません。")
            return()
        fName="EBDAS_"+recordDateTime+"_"+recordBaloonName+".csv"
        fDir=await page.client_storage.get_async("directory_path")+"/"+recordBaloonName
        try:
            with open(fDir+"/"+fName, 'w', encoding="utf_8_sig") as f:
                f.write(recordRawData)
        except FileNotFoundError:
            await openSnackbar("CSVファイルの保存に失敗しました。: ディレクトリが存在しません(FileNotFoundError)")
            
        except Exception as e:
            await openSnackbar("CSVファイルの保存に失敗しました。: "+str(e))
        else:
            await openSnackbar("CSVファイルを保存しました: "+fDir+"/"+fName)
            print("CSV Complete!")
            recordDeleteTitle.color=None
            recordDeleteText.color=None
            recordDeleteIcon.color=None
            await recordDeleteTitle.update_async()
            await recordDeleteText.update_async()
            await recordDeleteIcon.update_async()
        
    recordSaveTitle = ft.Text(value="保存", size=20)
    recordSaveText = ft.Text(value="保存対象?")
    recordSaveIcon = ft.Icon(name=ft.icons.SAVE)

    recordSaveButton = ft.ElevatedButton(
            content=ft.Container(
                content=ft.Row([
                    recordSaveIcon,
                    ft.Column(
                        [
                            recordSaveTitle,
                            recordSaveText,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=2,
                    )
                    ],
                    spacing=15,
                ),
                padding=ft.padding.all(5),
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            disabled=True,
            on_click=recordSave
        )

    async def recordDelete(e):
        global connectStatus, recordStatus, recordDataStatus, recordRawData, recordBaloonName, recordDateTime, recordStartTime, recordStartAltitude
        if recordStatus == True or recordDataStatus == False:
            await openSnackbar("記録中 または 記録データがありません。")
            return()
        recordStartTime=-1.0
        recordStartAltitude=0.0
        recordStatus=False
        recordDataStatus=False
        recordSaveButton.disabled=True
        recordDeleteButton.disabled=True
        recordDeleteTitle.color=None
        recordDeleteText.color=None
        recordDeleteIcon.color=None
        await recordDeleteButton.update_async()
        await recordSaveButton.update_async()

        # table.rows.clear() kx
        r_time.clear()
        r_temp.clear()
        r_pressure.clear()
        r_humidity.clear()
        r_altitude.clear()
        r_a0.clear()
        r_a1.clear()
        r_a2.clear()
        r_a3.clear()
        recordRawData=""
        rawRecorddata_tx.value=""
        for i in range(0, 9):
            rtNowData[i].value="-"
            rtNowData[i].on_click=lambda e: pyperclip.copy("-")
        if baloonSelecter.value != None and connectStatus==True and ((recordStatus==False and recordDataStatus==True) or recordDataStatus==False):
            recordStartButton.disabled=False
        else:
            recordStartButton.disabled=True
        await tempGraphSystem.reset()
        # await table.update_async() kx

        global recordStopWatchSystem
        recordTime=recordStopWatchSystem.stop()
        recordStopWatchSystem.reset()
        recordTimeView.value="-"
        await recordTimeView.update_async()
        await recordDeleteTitle.update_async()
        await recordDeleteText.update_async()
        await recordDeleteIcon.update_async()
        await table_column.update_async()
        await realtimeRecordTable.update_async()
        await recordStartButton.update_async()
        await recordSaveButton.update_async()
        await recordDeleteButton.update_async()
        await rawRecorddata_tx.update_async()
        await page.update_async()
        
    recordDeleteTitle = ft.Text(value="一時データ削除", size=20)
    recordDeleteText = ft.Text(value="削除してOK?")
    recordDeleteIcon = ft.Icon(name=ft.icons.DELETE)

    recordDeleteButton = ft.ElevatedButton(
            content=ft.Container(
                content=ft.Row([
                    recordDeleteIcon,
                    ft.Column(
                        [
                            recordDeleteTitle,
                            recordDeleteText,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=2,
                    )
                    ],
                    spacing=15,
                ),
                padding=ft.padding.all(5),
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            disabled=True,
            on_click=recordDelete
        )

        
    recordStartTitle = ft.Text(value="記録スタート", size=20)
    recordStartText = ft.Text(value="離陸時にクリック")
    recordStartIcon = ft.Icon(name=ft.icons.RADIO_BUTTON_CHECKED, color="red")
    
    async def recordStop(e):
        global recordStopWatchSystem
        recordTime=recordStopWatchSystem.stop()
        recordStopWatchSystem.reset()
        global connectStatus, recordStatus
        # if connectStatus == False:
        #     return()
        recordStatus = False
        recordStartButton.on_click=recordStart
        if recordDataStatus:
            recordSaveButton.disabled=False
            recordDeleteButton.disabled=False
            recordDeleteTitle.color="red"
            recordDeleteText.color="red"
            recordDeleteIcon.color="red"
            recordTimeView.value=recordTime
        else:
            recordSaveButton.disabled=True
            recordDeleteButton.disabled=True
        recordStartTitle.value="記録スタート"
        recordStartText.value="離陸時にクリック"
        recordStartTitle.color=None
        recordStartText.color=None
        recordStartIcon.name=ft.icons.RADIO_BUTTON_CHECKED
        recordStartButton.disabled=True
        await recordStartTitle.update_async()
        await recordStartText.update_async()
        await recordStartIcon.update_async()
        await recordStartButton.update_async()
        await recordSaveButton.update_async()
        await recordDeleteButton.update_async()
        await recordTimeView.update_async()
        await tempGraphSystem.set(time=r_time, temp=r_temp, pressure=r_pressure, humidity=r_humidity, altitude=r_altitude, a0=r_a0, a1=r_a1, a2=r_a2, a3=r_a3)
        await page.update_async()

    async def recordStart(e):
        recordStopWatchSystem.start()
        global connectStatus, recordStatus
        # if connectStatus == False:
        #     return()
        recordStatus = True
        recordStartButton.on_click=recordStop
        recordStartTitle.value="記録ストップ"
        recordStartText.value="着陸時にクリック"
        recordStartTitle.color="red"
        recordStartText.color="red"
        recordStartIcon.name=ft.icons.STOP
        await recordStartTitle.update_async()
        await recordStartText.update_async()
        await recordStartIcon.update_async()
        recordTimeView.value="記録中"
        await recordTimeView.update_async()
        await page.update_async()

        
    recordStartButton = ft.ElevatedButton(
            content=ft.Container(
                content=ft.Row([
                    recordStartIcon,
                    ft.Column(
                        [
                            recordStartTitle,
                            recordStartText,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=2,
                    )
                    ],
                    spacing=15,
                ),
                padding=ft.padding.all(5),
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=recordStart,
            disabled=True
        )

    rtBottomMenu=ft.Row(
        spacing=5,
        alignment=ft.alignment.center,
        controls=[
            # Text("EBDAS"),
            ft.IconButton(
                icon=ft.icons.REFRESH,
                # icon_color="blue400",
                # icon_size=20,
                tooltip="機材を再読み込み",
                on_click=reloadBaloons
            ),
            baloonSelecter,
            ft.Text("▶"),
            recordStartButton,
            ft.Text("▶"),
            recordSaveButton,
            ft.Text("▶"),
            recordDeleteButton,
        ],
    )
    body.append(rtBottomMenu)

    lv0.controls.append(table_column)
    body.append(lv0)
    
    realtimeTable=ft.DataTable(
        # border=ft.border.all(2, "red"),
        show_bottom_border=True,
        horizontal_margin=0, 
        #columns 里必须添加 DataColumn 类型的控件
        columns=[
            ft.DataColumn(ft.Text("時間[sec]"), numeric=True),
            ft.DataColumn(ft.Text("外気温度[℃]"), numeric=True),
            ft.DataColumn(ft.Text("圧力[hPa]"), numeric=True),
            ft.DataColumn(ft.Text("湿度[%]"), numeric=True),
            ft.DataColumn(ft.Text("標高[m]"), numeric=True),
            ft.DataColumn(ft.Text("a0[℃]"), numeric=True),
            ft.DataColumn(ft.Text("a1[℃]"), numeric=True),
            ft.DataColumn(ft.Text("a2[℃]"), numeric=True),
            ft.DataColumn(ft.Text("a3[℃]"), numeric=True),
        ],
        rows=[
                ft.DataRow([
                    ft.DataCell(realtimeData[0]),
                    ft.DataCell(realtimeData[1]),
                    ft.DataCell(realtimeData[2]),
                    ft.DataCell(realtimeData[3]),
                    ft.DataCell(realtimeData[4]),
                    ft.DataCell(realtimeData[5]),
                    ft.DataCell(realtimeData[6]),
                    ft.DataCell(realtimeData[7]),
                    ft.DataCell(realtimeData[8]),
                ]),
            ],
        )
    realtimeLv.controls.append(realtimeTable)
    rtTab.append(realtimeLv)
    
    realtimeRecordLv = ft.ListView(expand=1, spacing=10, padding=ft.padding.only(left=20, top=0, right=20, bottom=20), auto_scroll=False, on_scroll_interval=0)
    # lv.controls.append(lv0)
    realtimeRecordLv.controls.append(realtimeRecordTable)
    rtTab.append(realtimeRecordLv)

    lv = ft.ListView(expand=1, spacing=10, padding=ft.padding.only(left=20, top=0, right=20, bottom=20), auto_scroll=False, on_scroll_interval=0)
    # lv.controls.append(lv0)
    lv.controls.append(table)
    # body.append(lv)
    rawRecorddata_tx=ft.TextField(hint_text="Record data", border=ft.InputBorder.NONE, filled=True, multiline=True,min_lines=10,max_lines=10,  read_only=True, value="")
    body.append(rawRecorddata_tx)
    # await page.add_async(ft.Column(spacing=0, controls=[lv0, lv]))
    async def button_clicked(time):
        
        
        b=ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(time, selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("28.2", selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("993.4", selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("39.8", selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("167.0", selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("23.4", selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("23.5", selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("23.4", selectable=True, max_lines=1, no_wrap=True)),
                    ft.DataCell(ft.Text("23.4", selectable=True, max_lines=1, no_wrap=True)),
                    ])

        # table.rows.append(b) kx
        await page.update_async()
        print("按钮被点击")
        

    

    # body.append(ft.Row([rtAutoScSwitch, ft.Text("動作が重くなります! 記録は離陸中のみしてください。")], spacing=12))
    body.append(ft.Row([ft.Text("動作が重くなります! 記録は離陸中のみしてください。")], spacing=12))


    await page.add_async(menubaritem)

    # await page.add_async(Countdown(60))

    async def dataCopy(e):
        pyperclip.copy(rawdata_tx.value)
        await openSnackbar("コピーしました。")

    await page.add_async(dlg_modal)
    
    rawdata_tx=ft.TextField(hint_text="Raw data", border=ft.InputBorder.NONE, filled=True, multiline=True,min_lines=16,max_lines=16,  read_only=True, value="")
    
    tempGraphSystem= tempGraph()
    bodySide.append(tempGraphSystem)
    
    realtimeGraphSystem= tempGraph()
    rtTabSide.append(realtimeGraphSystem)
    

    ###################
    ## Divider System
    ###################

    async def move_vertical_divider(e: ft.DragUpdateEvent):
        global connectStatus
        if connectStatus:
            return()
        if (e.delta_x > 0 and tab0c.widtha() < 1500) or (e.delta_x < 0 and tab0c.widtha() > 800):
            await tab0c.widthPlus(e.delta_x)
        await tab0c.update_async()
        if (e.delta_x > 0 and tab1c.widtha() < 1500) or (e.delta_x < 0 and tab1c.widtha() > 800):
            await tab1c.widthPlus(e.delta_x)
        await tab1c.update_async()
        
    async def show_draggable_cursor(e: ft.HoverEvent):
        global connectStatus
        if connectStatus:
            return()
        e.control.mouse_cursor = ft.MouseCursor.RESIZE_LEFT_RIGHT
        await e.control.update_async()
        
    class c(ft.UserControl):
        def __init__(self, m, scroll):
            super().__init__()
            if scroll:
                self.control = ft.Container(
                    content=ft.Column(m, scroll="AUTO"),
                    alignment=ft.alignment.top_left,
                    width=900,
                    padding=ft.padding.only(top=8)
                    # expand=5,
                )
            else:
                self.control = ft.Container(
                    content=ft.Column(m),
                    alignment=ft.alignment.top_left,
                    width=900,
                    # expand=5,
                )
            
        async def widthPlus(self, x):
            self.control.width += x
            await self.control.update_async()
            
        def widtha(self):
            return self.control.width

        def build(self):
            return self.control


    def d(m):
        return ft.Container(
            content=ft.Column(m, scroll="AUTO"),
            alignment=ft.alignment.center,
            expand=2,
        )
    
    tab0c=c(rtTab, scroll=False)
    tab1c=c(body, scroll=True)
        
    Tab0=ft.Row(
        controls=[
            tab0c,
            ft.GestureDetector(
                content=ft.VerticalDivider(),
                drag_interval=10,
                on_pan_update=move_vertical_divider,
                on_hover=show_draggable_cursor,
            ),
            d(rtTabSide)
        ],
        spacing=0,
        width=400,
        height=400,
    )

    Tab1=ft.Row(
        controls=[
            tab1c,
            ft.GestureDetector(
                content=ft.VerticalDivider(),
                drag_interval=10,
                on_pan_update=move_vertical_divider,
                on_hover=show_draggable_cursor,
            ),
            d(bodySide)
        ],
        spacing=0,
        width=400,
        height=400,
    )
    
    t = ft.Tabs(
        selected_index=0,
        animation_duration=0,
        tabs=[
            ft.Tab(
                text="リアルタイム",
                icon=ft.icons.ANALYTICS_ROUNDED,
                content=Tab0
            ),
            ft.Tab(
                text="記録する",
                icon=ft.icons.EDIT_NOTE_ROUNDED,
                content=Tab1
            ),
            # ft.Tab(
            #     text="グラフ",
            #     icon=ft.icons.CALCULATE_ROUNDED,
            #     content=ft.Container(
            #         content=ft.Row(bodySide, scroll="AUTO"),
            #         alignment=ft.alignment.center,
            #         image_fit="CONTAIN",
            #         expand=1
            #         # expand=2,
            #     ),
            # ),
            # ft.Tab(
            #     text="計算機",
            #     icon=ft.icons.CALCULATE_ROUNDED,
            #     content=ft.Text("この機能はまだ実装されていません。"),
            # ),
            # ft.Tab(
            #     text="チェックリスト",
            #     icon=ft.icons.CHECK_BOX_ROUNDED,
            #     content=ft.Text("この機能はまだ実装されていません。"),
            # ),
            ft.Tab(
                text="生データ",
                icon=ft.icons.TEXT_FIELDS_ROUNDED,
                content=ft.Container(content=ft.Column([ElevatedButton("コピー", on_click=dataCopy), rawdata_tx], alignment=ft.MainAxisAlignment.START, expand=True),padding=ft.padding.only(top=8))
            ),
            ft.Tab(
                text="機材管理",
                icon=ft.icons.AIRPLANEMODE_ACTIVE_ROUNDED,
                content=ft.Container(content=ft.Column([ft.Column(controls=[option_textbox, add])], alignment=ft.MainAxisAlignment.START, expand=True),padding=ft.padding.only(top=8))
            ),
        ],
        expand=1,
    )



    await page.add_async(t)


ft.app(target=main, assets_dir="assets")