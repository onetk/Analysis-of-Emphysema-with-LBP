#coding:utf-8

"""
本プログラムは下記の論文内容を一部再現したものです.
使用するパッチ画像等は下記URLよりダウンロードしてください.
判別方法：ユークリッド距離から算出された画像同士の値をK最近傍法により分類

論文名
Quantitative Analysis of Pulmonary Emphysema Using Local Binary Patterns
URL
http://image.diku.dk/emphysema_database/
"""

#--------------------------------------------------------------------------#

# 入出力の為のライブラリ #
import cv2, csv
import glob, re
import math

def main():

  # 以下の4つのファイルを作成
  histfile= 'LBPykr_1_Histgram.csv'
  ykrfile = 'LBPykr_2_EuclidDis.csv'
  resfile = 'LBPykr_3_Similarity.csv'
  knnfile = 'LBPykr_4_KNN.csv'
  aknfile = 'LBPykr_5_diff_KNN.csv'
  
  # K Nearest Neighborの個数
  knum=20
	# パッチ画像のラベル閾値
  label_1=60
  label_2=110

  '''
  # 標準入力などの準備
  argvs =sys.argv
  try:
    os.mkdir('./temp')
  except:
    print('made temp file')
  '''

  # ヒストグラムの読み込みデータがあれば読み込み
  try:
    with open (histfile,'r')as fp:
      in_hist=list(csv.reader(fp))
      # convert list type(str->int)  in_hist[0]->256個, in_hist->168個
      histgram=[[int(elm) for elm in in_hist[0]] for in_hist[0] in in_hist]
    fp.close()

    # checking lists and display
    for x in range(len(histgram)):
      for y in range (len(histgram[1])-1):
        if histgram[x][y]!=0:
          print ('{:<9}'.format(str(y)+"->"+str(histgram[x][y])+",")),
      print ('\nReading: ' + str(x+1) + 'pic')
    print ('\nReading '+histfile)


  #--- 無ければデータ作成 ---#
  except:
    #--- 画像入力処理 ---#
    print ("Please input picture file")
    input_picture = raw_input('>>>  ')
    # sort input picture (画像の番号順に変換)
    file_list = sorted(glob.glob(input_picture+'/*'))
    file_list2 = [(re.search("[0-9]+", x).group(), x) for x in file_list]
    file_list2.sort(cmp = lambda x, y: cmp(int(x[0]), int(y[0])))
    file_list = [x[1] for x in file_list2]
    img_num=len(file_list)

    points=8
    radius=1
    histgram = [[0 for col in range(256)] for row in range(img_num)]

    for img_set in range (0,img_num):
      input_img = cv2.imread(file_list[img_set],0)
      img_hor = len(input_img)
      img_ver = len(input_img[0])
      lbp_img =  [[0 for col in range(img_ver)] for row in range(img_hor)]
      
      #--- LBP処理部分 ----------------------------------#
      for i in range(0,img_hor):
        for j in range(0,img_ver):     
          # reset array
          mask=[0 for col in range(points)]
          lbp_img[i][j]=2**points-1
          # when ( left / right / top / bottom ) exist, calc LBP
          if i>radius and i+radius<img_ver and  j>radius and j+radius<img_hor  :
            
            #--- LBP算出部分 ---#
            for part in range (0,points):
              # measure distance between [j][j] and its neighborhoods
              x_len = int(radius * math.cos(360/points * part)+0.5)
              y_len = int(radius * math.sin(360/points * part)+0.5)
              # get mask pattern -正負判定はsign()でもok-
              if input_img[i+x_len][j+y_len] - input_img[i][j] > 0:
                mask[part] =1
            #print ('\n'+str(mask))
                 
            # loop time to find min value
            for k in range (0,points):
              lbp_val=0              
              for x in range (0+k,points):
                lbp_val += mask[x]* (2**(x-k))
              for y in range (0,k):
                lbp_val += mask[y]* (2**(y+(points-k)))
              #print ('val: '+str(lbp_img[i][j])),
              lbp_img[i][j]=min(lbp_img[i][j],lbp_val)
              #print ('-> '+str(lbp_img[i][j]))


            # 256色の濃淡レベルに変換後, 格納
            #lbp_img[i][j] = int(lbp_val/(2**abs(8-points)))

      #---- end LBP loop --------------------------------#
 
      '''    
      #--- LBP画像保存 ---#
      save_name ='/temp/patch'+str(img_set-1)+'.tiff'
      cv2.imwrite (save_name,save_img)
      print ('\nsave image file'+save_name)
      '''

      #--- ヒストグラム作成 ---#
      for v in range(0,img_ver):
        for h in range(0,img_hor):     
          histgram[img_set-1][lbp_img[v][h]] += 1
      
      for v2 in range(256):
        if histgram[img_set-1][v2]!=0:
          print ('{:<9}'
          .format(str(v2)+"->"+str(histgram[img_set-1][v2])+",")),  
      print ('\nReading: ' + file_list[img_set])
    
    #---- end img_set roop ---------------------------------#
    
    
    #--- ヒストグラム結果 書き込み部分 ---#
    with open(histfile,'w') as f:
      writer = csv.writer(f)
      writer.writerows(histgram)
    f.close()


  #---- end histgram making ------------------------------------------#


  #--- ユークリッド距離算出部分 ---#
  ykr = [[0 for col in range(len(histgram))] for row in range(len(histgram))]
  
  for i in range(len(histgram)):
    for j in range(len(histgram)):      
      diff=0
      for k in range(len(histgram[0])):
        if histgram[i][k] or histgram[j][k] :
          diff += ((histgram[i][k]-histgram[j][k])**2)
      ykr[i][j] = math.sqrt(diff)  
  print ('making Euclidean distance file')

  try:
    with open(ykrfile,'w') as fy:
      writer = csv.writer(fy)
      writer.writerows(ykr)
    fy.close()
  except:
    print ('\nerror!\nabout: file ' + ykrfile )


  #--- ユークリッド距離からの類似度判定部分 ---#
  res = [[0 for col in range(len(histgram))] for row in range(len(histgram))]
  for i in range(len(ykr)):
    # array for sorting (2*168) 
    sorter = [[0 for col in range(2)]  for row in range(len(ykr))]
    for j in range(len(ykr)):
      sorter[j][0]=j
      sorter[j][1]=ykr[i][j]
    # Sort in Euclidean distance descending order
    sorter.sort(key=lambda x:x[1])#,reverse=True)
    for k in range(len(ykr)):
      res[i][k]=sorter[k][0]

  #- ソート結果出力用 -#
  try:
    with open(resfile,'w') as fr:
      writer = csv.writer(fr)
      writer.writerows(res)
    fr.close()
  except:
    print ('\nerror!\nabout: file ' + resfile )

  #- 類似度順の表示部分 -#
  for i in range(len(ykr)):
    for j in range(1,10):
      print ('{:<5}'
        .format(str(int(res[i][j]))+" >")),    
    print ('\nSimilarity: ' + str(i+1) + 'pic')
  print('try K Nearest Neighbor')

  #--- K最近傍法によるラベル判定 ---#
  # image #0-59:NT, 60-109:CLE, 110-168:PSE 
  #print ('temp\n How many k?')
  #knum=int(raw_input('>>>')) 
  knum=len(ykr)
  all_knn = [0 for col in range(knum)]
  max_accus = 0.0

  for knum in range (knum):
    knn = [[0 for col in range(2)]  for row in range(len(ykr))]
    accu=0.0
    for i in range(len(ykr)):
      # patch -> NT(#0),CLE(#1),PSE(#2) class
      PatchClass = [[0 for col in range(2)] for row in range(3)]
      for dep in range(3):
        PatchClass[dep][0]=dep
   
      for j in range(1,knum+1):
        if res[i][j]<label_1:
          PatchClass[0][1]+=1
        elif res[i][j]<label_2:
          PatchClass[1][1]+=1
        else:
          PatchClass[2][1]+=1
      # 3種の中で一番高いものノラベルに推定
      if PatchClass[0][1]>PatchClass[1][1] and PatchClass[0][1]>PatchClass[2][1]:
        knn[i][1]=1
      elif PatchClass[1][1]>PatchClass[0][1] and PatchClass[1][1]>PatchClass[2][1]:
        knn[i][1]=2
      #else:
       # knn[i][1]=3
      
      elif PatchClass[2][1]>PatchClass[0][1] and PatchClass[2][1]>PatchClass[1][1]:
        knn[i][1]=3
      # 同値だった場合の処理(同値が解消されるまでkの値を延長)
      else:    
        PatchClass.sort(key=lambda x:x[1])
        add=1
        while PatchClass[0][1]==PatchClass[1][1]:    
          if res[i][knum+add]<label_1:
            for a in range(0,3):
              if PatchClass[a][0]==0:
                PatchClass[a][1]+=1
          elif res[i][knum+add]<label_2:
            for a in range(0,3):
              if PatchClass[a][0]==1:
                PatchClass[a][1]+=1
          else:
            for a in range(0,3):
              if PatchClass[a][0]==2:
                PatchClass[a][1]+=1
          add+=1  
          PatchClass.sort(key=lambda x:x[1])
        knn[i][1]=PatchClass[1][0]+1
      
      # ラベル付け (上記URLより)
      if i<label_1:
        knn[i][0]=1
      elif i<label_2:
        knn[i][0]=2
      else:
        knn[i][0]=3
      # ラベルと合致していたら精度++
      if knn[i][0]==knn[i][1]:
        accu+=1
    accu/=len(ykr)
    all_knn[knum]=accu
    if max_accus < accu:
      max_accus=accu
      max_accu_num=knum
    
  # K Nearest Neighborファイルの出力用
  try:
    with open(knnfile,'w') as fk:
      writer = csv.writer(fk)
      writer.writerows(knn)
    fk.close()
  except:
    print ('\nerror!\nabout: file ' + knnfile )
  
  # all_knnファイルの出力用 #
  try:
    with open(aknfile,'w') as fa:
      writer = csv.writer(fa)
      writer.writerow(all_knn)
    fa.close()
  except:
    print ('\nerror!\nabout: file ' + aknfile )

  print ('\nMax accuracy: #'+str(max_accu_num-1)+' '+str(max_accus)+'\n\nfinish')

#---- fin main function -------------------------------------------------

if __name__ == '__main__':
    main()


#--------------------------------------------------------------------------#

__author__ = "Taka.N"
__version__ = "0.8"
__date__    = "19 January 2018"

