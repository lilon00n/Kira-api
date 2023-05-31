import cv2
import numpy as np

# load image
img = cv2.imread('input/colores_2pms(Yellow).tif')
# rsz_img = cv2.resize(img, None, fx=0.25, fy=0.25)  # resize since image is huge
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grayscale

# threshold to get just the signature
retval, thresh_gray = cv2.threshold(
    gray, thresh=200, maxval=255, type=cv2.THRESH_BINARY)

# find where the signature is and make a cropped region
points = np.argwhere(thresh_gray == 0)  # find where the black pixels are
# store them in x,y coordinates instead of row,col indices
points = np.fliplr(points)
x, y, w, h = cv2.boundingRect(points)  # create a rectangle around those points

print(x)
print(y)
print(w)
print(h)
# x, y, w, h = x-10, y-10, w+20, h+20  # make the box a little bigger
crop = gray[y:y+h, x:x+w]  # create a cropped region of the gray image


# get the thresholded crop
retval, thresh_crop = cv2.threshold(
    crop, thresh=200, maxval=255, type=cv2.THRESH_BINARY)

# display
cv2.imshow("Cropped and thresholded image", thresh_crop)
cv2.waitKey(0)
