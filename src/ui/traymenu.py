# ./ui/traymenu.py
"""
基于TinUI的Tray菜单
"""
from tkinter import Toplevel
from tinui.TinUI import TinUINum, BasicTinUI

class QuickUpTrayMenu:
    def __init__(self, master):
        self.master = master
    def create_menubar(self,font='微软雅黑 10',fg='#1b1b1b',bg='#fbfbfc',line='#cccccc',activefg='#191919',activebg='#f0f0f0',activeline='#f0f0f0',onfg='#5d5d5d',onbg='#f5f5f5',online='#e5e5e5',cont=()):
        def endy():
            pos=bar.bbox('all')
            return 0 if pos==None else pos[3]+10
        def repaint():
            for back in backs:
                pos=bar.bbox(back[0])
                bar_coords = (5,pos[1]+4.5,maxwidth+5-4.5,pos[1]+4.5,maxwidth+5-4.5,pos[3]-4.5,5,pos[3]-4.5)
                bar_coords_2 = (6,pos[1]+5.5,maxwidth+4-4.5,pos[1]+5.5,maxwidth+4-4.5,pos[3]-5.5,6,pos[3]-5.5)
                bar.coords(back[0], bar_coords_2)
                bar.coords(back[1], bar_coords)
        def readyshow():
            allpos=bar.bbox('all')
            winw=allpos[2]-allpos[0]+35
            winh=allpos[3]-allpos[1]+35
            maxx=menu.winfo_screenwidth()
            maxy=menu.winfo_screenheight()
            wind.data=(maxx,maxy,winw,winh)
            bar.move('all',0,14)
        def show(x,y):
            maxx,maxy,winw,winh=wind.data
            if x+winw>maxx:
                x=x-winw
            if y+winh>maxy:
                y=y-winh
            menu.geometry(f'{winw+30}x{winh+20}+{x}+{y}')
            menu.attributes('-alpha',0)
            menu.deiconify()
            it = 0
            for i in (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1):
                menu.after(it*20, lambda alpha=i : __show(alpha))
                it += 1
        def __show(alpha):
            menu.attributes('-alpha',alpha)
            menu.update_idletasks()
            if alpha == 1:
                menu.focus_force()
        menu=Toplevel(self.master)
        menu.withdraw()
        menu.bind('<FocusOut>',lambda event:menu.withdraw())
        menu.attributes('-topmost',1)
        menu.overrideredirect(True)
        bar=BasicTinUI(menu,bg='#01FF11')
        bar.pack(fill='both',expand=True)
        wind=TinUINum()
        backs=[]
        widths=[]
        for i in cont:
            button=bar.add_button2((0,endy()-13),i[0],None,'',fg,bg,bg,3,activefg,activebg,activeline,onfg,onbg,online,font=font,command=lambda event,i=i:(menu.withdraw(),i[1]()))
            backs.append((button[1],button[2]))
            pos=bar.bbox(button[1])
            widths.append(pos[2]-pos[0])
        maxwidth=max(widths)
        repaint()
        readyshow()
        backs.clear()
        widths.clear()
        bbox=bar.bbox('all')
        x1=bbox[0]
        x2=bbox[0]+maxwidth+8
        gomap=(x1+5,bbox[1]+5,x2-5,bbox[1]+5,x2-5,bbox[3]-5,x1+5,bbox[3]-5)
        mback=bar.create_polygon(gomap,fill=bg,outline=bg,width=17)
        gomap=(x1+4,bbox[1]+4,x2-4,bbox[1]+4,x2-4,bbox[3]-4,x1+4,bbox[3]-4)
        mline=bar.create_polygon(gomap,fill=bg,outline=line,width=17)
        bar.lower(mback)
        bar.lower(mline)
        bar.move('all',12,5)
        menu.attributes('-transparent','#01FF11')
        return show