#cPng2png
import cv2
import numpy as np
import os
import glob
from lxml import etree


svgbase = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5120 5120">
</svg>
'''
colorDic = {
    "main": "#010A21",
    "main2": "#041648",
    "color1": "#0231A2",
    "color2": "#1E64F4",
    "light1": "#53B0FE",
    "light2": "#9ED3FE",
    "accent1": "#7A8CFF",

    "back": "#FFFFFF"
}
#色辞書palettDicをbgr配列化
colorList = []
for k, v in colorDic.items():
    colorList.append([int(v[5:7],16),int(v[3:5],16),int(v[1:3],16)])#rgbをbgrにして各色取り出し

#フォルダ名づけ用の色名配列作成
colorDicList = list(colorDic.keys())
colorCodeList = list(colorDic.values())


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

#階調化画像と色リストから黒シルエットsvgを色数ぶん保存する関数
def gradDevider(image,colorList,colorDicList,file):
    root = etree.fromstring(svgbase)
    for index, palette in enumerate(colorList):
        if colorDicList[index] != "back":
        
            themec = np.array(colorList[index])  # 抽出する色(bgr)
            extract = cv2.inRange(image, themec, themec) #色の幅ゼロで色抽出
            extract = cv2.bitwise_not(extract) #白黒反転
            if not os.path.exists("SVGs"):
                os.mkdir("SVGs")
                        
            dirname = str(colorDicList[index]+colorCodeList[index][1:])
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            #png
            name = os.path.splitext(file)[0]
            cv2.imwrite(os.path.join(dirname, name+".png"),extract)  # 画像の保存
            # os.system("potrace -s " + os.path.join(dirname, name+".bmp")) #bmp -> svg
            # os.system("del " + os.path.join(dirname, name+".bmp"))
        

        if colorDicList[index] != "back":
            
            dirname = str(colorDicList[index])
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            #bmpを書いてsvgに変換
            name = os.path.splitext(file)[0]
            cv2.imwrite(os.path.join(dirname, name+".bmp"),extract)  # 画像の保存
            os.system("potrace -s " + os.path.join(dirname, name+".bmp")) #bmp -> svg
            os.system("del " + os.path.join(dirname, name+".bmp"))
            
            # baseSVGをパースする
            baseSVG = etree.parse("./"+colorDicList[0]+"/"+name+".svg")
            g = baseSVG.find('.//svg:g', namespaces={"svg": "http://www.w3.org/2000/svg"})
            
            # b.svgからpath要素を抜き出す
            b_tree = etree.parse(os.path.join(dirname, name+".svg"))
            paths = b_tree.xpath('//svg:path', namespaces={"svg": "http://www.w3.org/2000/svg"})
            # path要素にfill属性を追加して、g要素に加える
            for path in paths:
                path.set('fill', colorCodeList[index])
                #g.append(path)
                root.append(path)
            # a.svgに書き込む
            with open("./SVGs/"+name+".svg", "wb") as f:
                f.write(etree.tostring(root))
        
    
#####################実行########################



#色空間で最近傍の色を対応付けるボロノイ写像マップをつくる
boronoi = makeBoronoi(colorList)

files = glob.glob("*.png")

for index, file in enumerate(files):
    img = cv2.imread(file)
    # img = cv2.flip(img, 0)
    h, w = img.shape[:2]
    img = cv2.flip(img, 0)

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
    print(str(file) + " " + str(index+1) + "/" + str(len(files)))


