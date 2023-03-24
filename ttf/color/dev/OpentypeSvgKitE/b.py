#cPng2png


import os
import glob

svgbase = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5120 5120">
</svg>
'''
colorDic = {
    "main": "#111111",
    "c1":"#19285D",
    "c2":"#465850",
    "c3":"#0E5E3F",
    "c4":"#83D280",
    "c5":"#AEE146",
    "c6":"#4DAE5B",
    "c7":"#3B7468",
    "c8":"#F05D2A",
    "c9":"#C3CBB3",
    "c10":"#386A76",
    "c11":"#81A922",
    "c12":"#738488",
    "c13":"#424C54",
    "c14":"#2F5238",
    "c15":"#757986",
    "C16":"#546B60",

    "back": "#FFFFFF"
}
fontname = "base"
familyname = "base"
#色辞書palettDicをbgr配列化
colorList = []
for k, v in colorDic.items():
    colorList.append([int(v[5:7],16),int(v[3:5],16),int(v[1:3],16)])#rgbをbgrにして各色取り出し

#フォルダ名づけ用の色名配列作成
colorDicList = list(colorDic.keys())
colorCodeList = list(colorDic.values())

def main():
    import numpy as np
    import cv2
    from lxml import etree

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

    os.system("ffpython b1.py")

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
        print(str(file) + " " + str(index+1) + "/" + str(len(files)))
    os.system("ffpython b2.py")
    os.system("python b3.py")

if __name__ == '__main__':
    main()


