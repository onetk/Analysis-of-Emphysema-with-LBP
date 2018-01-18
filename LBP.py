#coding:utf-8
# 入出力の為のライブラリ #
import cv2
import copy
import math

def main():
  #--- 画像入力処理 ---#
  print ("Please input picture")
  input_picture = raw_input('>>>  ')
  input_img = cv2.imread(input_picture,0)
  lbp_img = copy.deepcopy(input_img)
  
  img_hor = len(input_img)
  img_ver = len(input_img[0])
  histgram = [0 for col in range(256)]
  points=8
  radius=1

  #--- LBP処理部分 ---#
  for i in range(0,img_hor):
    for j in range(0,img_ver):     
      # reset array
      mask=[0 for col in range(points)]
      lbp_img[i][j]=2**8-1
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
             
        # loop time to find min value
        print(mask)
        for k in range (0,points):
          lbp_val=0              
          for x in range (0+k,points):
            lbp_val += mask[x]* (2**(x-k))
          for y in range (0,k):
            lbp_val += mask[y]* (2**(y+(points-k)))
          lbp_img[i][j]=min(lbp_img[i][j],lbp_val)
          print (lbp_img[i][j])

  #--- ヒストグラム作成 ---#
  for i in range(0,img_hor):
    for j in range(0,img_ver):     
      histgram[lbp_img[i][j]] += 1


  #--- 結果表示部分 ---#
  cv2.imshow("Local Binary Pattern",lbp_img)
  # when input key was 's', save result image or fin
  if cv2.waitKey(0) == ord('s'): 
    cv2.imwrite("LBP.png", lbp_img)
  cv2.destroyAllWindow()

# fin main function

if __name__ == '__main__':
    main()
