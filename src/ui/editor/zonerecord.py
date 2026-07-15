"""
编辑器 - 窗口捕获弹窗
"""
from tinui import TinUIXml
from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

from ui.utils import set_window_dark


zone_record_xml = ""
record_zone = True
record_round = True

def check_zone(tag):
    global record_zone
    record_zone = tag
    if not tag:
        round_check_func.off()

def check_round(tag):
    global record_round
    record_round = tag

funcs_dict = {
    'check_zone': check_zone,
    'check_round': check_round,
}

def onclose():
    pass


zone_check_func = None
round_check_func = None

def get_dialog(parent, theme:str):
    global zone_record_xml, zone_check_func, round_check_func
    if zone_record_xml == "":
        with open("ui-asset/editor-zone-record.xml", "r", encoding="utf-8") as f:
            zone_record_xml = f.read()

    d = Dialog(parent, 'xml', theme=theme)
    d.initial_xml_load("记录应用", zone_record_xml, funcdict=funcs_dict,
                       yescallback=onclose, nocallback=onclose, nonecallback=onclose,
                       tinuitheme=TinUIDark if theme == "dark" else TinUILight)
    uixml:TinUIXml = d.tinuixml

    zone_check_func = zone_check = uixml.tags['zonecheck'][-2]
    zone_check.on()
    round_check_func = round_check = uixml.tags['roundcheck'][-2]
    round_check.on()

    if theme == "dark":
        d.update_idletasks()
        set_window_dark(d)
    dr = d.initial_xml_init()
    return dr, record_zone, record_round
