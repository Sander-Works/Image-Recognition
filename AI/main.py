import cv2
import pytesseract
import numpy as np
from matplotlib import pyplot as plt
from imutils.object_detection import non_max_suppression

pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\Sondre\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'
#image = cv2.imread('nor_kvitt2.jpg')
#args = {"image":"nor_kvitt2,jpg", "east":"../input/text-detection/east_text_detection.pb", "min_confidence":0.5, "width":320, "height":320}
#image = cv2.imread(args['image'])

image = cv2.imread('C:/Users/Sondre/Desktop/vy.jpg')
east = "C:/Users/Sondre/Desktop/frozen_east_text_detection.pb"
newW = 640
newH = 480
min_confidence = 0.5


# Saving a original image and shape
orig = image.copy()
(origH, origW) = image.shape[:2]

# set the new height and width to default 320 by using args #dictionary.
#(newW, newH) = (args["width"], args["height"])

# Calculate the ratio between original and new image for both height and weight.
# This ratio will be used to translate bounding box location on the original image.
rW = origW / float(newW)
rH = origH / float(newH)

# resize the original image to new dimensions
image = cv2.resize(image, (newW, newH))
(H, W) = image.shape[:2]

# construct a blob from the image to forward pass it to EAST model
blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
                             (123.68, 116.78, 103.94), swapRB=True, crop=False)


# load the pre-trained EAST model for text detection
net = cv2.dnn.readNet(east)

# We would like to get two outputs from the EAST model.
#1. Probabilty scores for the region whether that contains text or not.
#2. Geometry of the text -- Coordinates of the bounding box detecting a text
# The following two layer need to pulled from EAST model for achieving this.
layerNames = [
	"feature_fusion/Conv_7/Sigmoid",
	"feature_fusion/concat_3"]

#Forward pass the blob from the image to get the desired output layers
net.setInput(blob)
(scores, geometry) = net.forward(layerNames)




## Returns a bounding box and probability score if it is more than minimum confidence
def predictions(prob_score, geo):
    (numR, numC) = prob_score.shape[2:4]
    boxes = []
    confidence_val = []

    # loop over rows
    for y in range(0, numR):
        scoresData = prob_score[0, 0, y]
        x0 = geo[0, 0, y]
        x1 = geo[0, 1, y]
        x2 = geo[0, 2, y]
        x3 = geo[0, 3, y]
        anglesData = geo[0, 4, y]

        # loop over the number of columns
        for i in range(0, numC):
            if scoresData[i] < min_confidence:
                continue

            (offX, offY) = (i * 4.0, y * 4.0)

            # extracting the rotation angle for the prediction and computing the sine and cosine
            angle = anglesData[i]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # using the geo volume to get the dimensions of the bounding box
            h = x0[i] + x2[i]
            w = x1[i] + x3[i]

            # compute start and end for the text pred bbox
            endX = int(offX + (cos * x1[i]) + (sin * x2[i]))
            endY = int(offY - (sin * x1[i]) + (cos * x2[i]))
            startX = int(endX - w)
            startY = int(endY - h)

            boxes.append((startX, startY, endX, endY))
            confidence_val.append(scoresData[i])

    # return bounding boxes and associated confidence_val
    return (boxes, confidence_val)

# Find predictions and  apply non-maxima suppression
(boxes, confidence_val) = predictions(scores, geometry)
boxes = non_max_suppression(np.array(boxes), probs=confidence_val)


##Text Detection and Recognition

# initialize the list of results
results = []

# loop over the bounding boxes to find the coordinate of bounding boxes
for (startX, startY, endX, endY) in boxes:
    # scale the coordinates based on the respective ratios in order to reflect bounding box on the original image
    startX = int(startX * rW)
    startY = int(startY * rH)
    endX = int(endX * rW)
    endY = int(endY * rH)

    # extract the region of interest
    r = orig[startY:endY, startX:endX]

    # configuration setting to convert image to string.
    configuration = "-l nor  --psm 4"
    ##This will recognize the text from the image of bounding box
    text = pytesseract.image_to_string(r, config=configuration)

    # append bbox coordinate and associated text to the list of results
    results.append(((startX, startY, endX, endY), text))

# Display the image with bounding box and recognized text
orig_image = orig.copy()

# Moving over the results and display on the image
for ((start_X, start_Y, end_X, end_Y), text) in results:
    # display the text detected by Tesseract
    print("{}\n".format(text))

    # Displaying text
    text = "".join([x if ord(x) < 128 else "" for x in text]).strip()
    cv2.rectangle(orig_image, (start_X, start_Y), (end_X, end_Y),
                  (0, 0, 255), 2)
    cv2.putText(orig_image, text, (start_X, start_Y - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

plt.imshow(orig_image)
plt.title('Output')
plt.show()
