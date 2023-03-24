"""
cpng2cttf
"""
import os
import glob
import fontforge #fontforgeをインストールしてbinフォルダにpath通したあとffpython hoge.py のようなコードで実行


import b

#色辞書palettDicをbgr配列化
colorList = []
for k, v in b.colorDic.items():
    colorList.append([int(v[5:7],16),int(v[3:5],16),int(v[1:3],16)])#rgbをbgrにして各色取り出し
#フォルダ名づけ用の色名配列作成
colorDicList = list(b.colorDic.keys())
colorCodeList = list(b.colorDic.values())

for i in range(len(colorDicList)):
    if colorDicList[i] != "back":
        font = fontforge.font()
        # 名前の設定
        fontname = colorDicList[i]
        font.fontname   = fontname
        font.fondname   = fontname
        font.fullname   = fontname
        font.familyname = fontname
        font.encoding   = "UnicodeFull"
        font.version    = "1.0"

        # pngs = glob.glob("./"+colorDicList[i]+colorCodeList[i][1:]+"/*.png")
        path = colorDicList[i]+colorCodeList[i][1:]+"/"
        pngs2names = lambda png : os.path.splitext(png)[0]
        pngs = glob.glob(path + "*.png")
        names = list(map(pngs2names, pngs))
        for index, name in enumerate(names):
            os.system("magick " + name+".png " + name+".bmp") #png -> bmp
            os.system("potrace -s " + name+".bmp") #bmp -> svg
            
            hexCodepoint = os.path.basename(name)[3:] #uni0041 -> 0041
            glyph = font.createMappedChar(int("0x"+hexCodepoint, 16))
            glyph.importOutlines(name+".svg") 
            if glyph.changed ==0: #importOutlinesに失敗したとき0、それ以外で1を返す
                glyph.importOutlines("0.svg")
                print("alternative 0.svg has been added")


            #上に140移動を追加
            
            os.system("del " + name+".bmp") #Tatsutori atowo nigosazu
            os.system("del " + name+".svg")
            print(str(index + 1)+"/"+str(len(names)))

        font.generate(fontname + '.ttf')
        font.close()



# os.system("fonts2svg -c 000000,ff9906,ef2218 color1.ttf color2.ttf light1.ttf")
def commandMaker(colorList,colorCodeList):
    command = "fonts2svg -c "
    for i in range(len(colorList)):
        if colorDicList[i] != "back":
            if i != 0:
                command += ","
            # else:
            #     command += "
            command += colorCodeList[i][1:].lower()

    for i in range(len(colorList)):
        if colorDicList[i] != "back":
            command += " "
            command += colorDicList[i] + ".ttf"

    #"fonts2svg -c 000000,ff9906,ef2218 color1.ttf color2.ttf light1.ttf"
    return command
print(commandMaker(colorList,colorCodeList))
os.system(commandMaker(colorList,colorCodeList))
os.system("addsvg SVGs base.ttf")




