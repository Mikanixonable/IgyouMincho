#cPng2png
import cv2
import numpy as np
import os
import glob
from lxml import etree
os.system("ffpython 1.py")

svgbase = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5120 5120">
</svg>
'''
colorDic = {
    "main": "#000001",
    "main2": "#0D3B94", #b1
    "color1": "#2B8AFA", #b2
    "color2": "#24ACFC", #b3
    "light1": "#55CC98", #lbg
    "light2": "#FC6FA2", #pink
    "accent1": "#9B9EA0", #gray
    "accent2": "#FA6F5C", #red
    "accent3": "#FAB52E", #yel
    "accent4": "#115564", #dg
    "accent5": "#ED573F", #r
    "accent6": "#1B93AB", #bg

    "back": "#FFFFFF"
}
# colorDic = {
#     "main": "#000001",
#     "main2": "#1A9E65", #gre
#     "color1": "#013562", #ai
#     "color2": "#5CE3DF", #lb
#     "light1": "#75A8FF", #sb
#     "light2": "#AAEE63", #lg
#     "accent1": "#D244CA", #pu
#     "accent2": "#00525D", #dg
#     "accent3": "#000B51", #aipu
#     "accent4": "#124495", #dmb
#     "accent5": "#FED660", #yelow
#     "accent6": "#A4A5A6", #gray
#     "accent7": "#9EC6BC", #lwg
#     "accent8": "#DC4C70", #red

#     "back": "#FFFFFF"
# }
#色辞書palettDicをbgr配列化
colorList = []
for k, v in colorDic.items():
    colorList.append([int(v[5:7],16),int(v[3:5],16),int(v[1:3],16)])#rgbをbgrにして各色取り出し

#フォルダ名づけ用の色名配列作成
colorDicList = list(colorDic.keys())
colorCodeList = list(colorDic.values())
# colorDic = {
#     "main": "#00000C",
#     "sub1": "#09AFCE",
#     "sub2": "#286BE7",
#     "light1": "#6D7173",
#     "light2": "#EC573F",
#     "light2": "#FDEC5A",
#     "back": "#FFFFFF"
# }

#色と色の二乗距離を計算する関数
def cLength(arr1,arr2):
    return (arr1[0]-arr2[0])**2 + (arr1[1]-arr2[1])**2 + (arr1[2]-arr2[2])**2

#色を与えるとパレットの中から一番近い色を返す関数
def cSelect(color,palettes):
    lengArr = []
    for palette in palettes:
        lengArr.append(cLength(palette,color))
    fillc = palettes[lengArr.index(min(lengArr))]
    return fillc

#階調化に必要な色のボロノイマップ対応辞書をつくる関数。軽量化のため色空間32立方をまとめて1つの写像。フルカラーで8*8*8個
def makeBoronoi(palettes):
    boronoiMap = [[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)]
    for bi, bv in enumerate(boronoiMap):
        for gi, gv in enumerate(bv):
            for ri, rv in enumerate(gv):
                boronoiMap[bi][gi][ri] = cSelect([bi*32,gi*32,ri*32],palettes)
    return boronoiMap

#色を与えると色対応辞書から近い色を返す関数
def cSelect2(color,boronoiMap):
    x = color[0]//32
    y = color[1]//32
    z = color[2]//32
    return boronoiMap[x][y][z]

#階調化画像と色リストから黒pngを色数ぶん保存する関数

def gradDevider(image,colorList,colorDicList,file):
    root = etree.fromstring(svgbase)
    for index, palette in enumerate(colorList):
        if colorDicList[index] != "back":
        
            themec = np.array(colorList[index])  # 抽出する色(bgr)
            extract = cv2.inRange(image, themec, themec) #色の幅ゼロで色抽出
            extract = cv2.bitwise_not(extract) #白黒反転
            # if not os.path.exists("SVGs"):
            #     os.mkdir("SVGs")
                        
            dirname = str(colorDicList[index]+colorCodeList[index][1:])
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            #png
            name = os.path.splitext(file)[0]
            cv2.imwrite(os.path.join(dirname, name+".png"),extract)  # 画像の保存
        
    
#####################実行########################



#色空間で最近傍の色を対応付けるボロノイ写像マップをつくる
boronoi = makeBoronoi(colorList)

files = glob.glob("*.png")

for index, file in enumerate(files):
    img = cv2.imread(file)
    # img = cv2.flip(img, 0)
    h, w = img.shape[:2]

    # 階調化
    for i in range(h):
        for j in range(w):
            b, g, r = img[i, j]
        
            img[i, j] = cSelect2([b,g,r],boronoi)
    if not os.path.exists("pngs"):
        os.mkdir("pngs")
    cv2.imwrite("./pngs/"+file,img)
    # 色ごとに分離
    gradDevider(img,colorList,colorDicList,file)
    print(str(file) + "disassembled " + str(index+1) + "/" + str(len(files)))
os.system("ffpython 2.py")


