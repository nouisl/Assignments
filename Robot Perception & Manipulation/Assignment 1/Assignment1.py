# Noushin Islam
# Assignment 1 - COMP 341
# some of the code from the OpenCV PCA implementation and Lab4 material have been used 

# import required libraries 
import cv2
import random
import torchvision
import numpy as np
import torch
import time
import matplotlib.pylab as plt

# disable gradient computation
torch.set_grad_enabled(False)
# set matplotlib properties
plt.rcParams["axes.grid"] = False

# function to draw an arrow on an image between two points, 
def drawAxis(img, p_, q_, colour, scale):
    # convert input points to lists
    p = list(p_)
    q = list(q_)
    
    # calculaze angle between the two points in radians
    angle = np.arctan2(p[1] - q[1], p[0] - q[0]) 
    # calculate distance between the two points
    hypotenuse = np.sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
    # lengthen the arrow by a factor of scale
    q[0] = p[0] - scale * hypotenuse * np.cos(angle)
    q[1] = p[1] - scale * hypotenuse * np.sin(angle)
    # draw a line between the two points 
    cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)
    # create the arrow hooks
    p[0] = q[0] + 9 * np.cos(angle + np.pi / 4)
    p[1] = q[1] + 9 * np.sin(angle + np.pi / 4)
    cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)
    p[0] = q[0] + 9 * np.cos(angle - np.pi / 4)
    p[1] = q[1] + 9 * np.sin(angle - np.pi / 4)
    cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)
    
# load a pre-trained Mask R-CNN model from torchvision
model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
model = model.eval().cpu()

# start video stream
stream = cv2.VideoCapture(0)
cv2.namedWindow("Result")

# image counter
img_counter = 0

# start infinite loop
while True:
    # read frame from the stream
    ret, frame = stream.read()
    # error handling
    if not ret:
        print("failed to grab frame")
        break

    # record the time 
    t = time.time()
    # convert image to a tensor
    image = frame
    image_tensor = torchvision.transforms.functional.to_tensor(image).cpu()
    # output of the model on the image
    output = model([image_tensor])[0]
    print('executed in %.3fs' % (time.time() - t))

    # using the coco benchmark dataset and defining colors
    coco_names = ['unlabeled', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'street sign', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'hat', 'backpack', 'umbrella', 'shoe', 'eye glasses', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'plate', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'mirror', 'dining table', 'window', 'desk', 'toilet', 'door', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'blender', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in coco_names]

    # create copy of image
    result_image = np.array(image.copy())
    # initialize empty list
    masks = []   
    
    # loop through the output boxes, labels, scores, and masks
    for box, label, score, mask in zip(output['boxes'], output['labels'], output['scores'], output['masks']):
        # draw the object if score is higher than 0.5
        if score > 0.5:
            # choose random color
            color = random.choice(colors)
            # convert mask to numpy array
            mask = mask[0].numpy()
            # threshold the mask
            mask = np.where(mask > 0.5, 1, 0).astype(np.uint8)
            # find the contours of the map and loop through it
            contours,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for i, c in enumerate(contours):
                # draw contours on result image
                cv2.drawContours(result_image,[contours[i]],-1,color,-1)
                alpha = 0.5
                result_image = cv2.addWeighted(result_image, alpha, image.copy(), 1-alpha,0, result_image)

                # get data points of the contour
                sz = len(c)
                data_pts = np.empty((sz, 2), dtype=np.float64)
                for i in range(data_pts.shape[0]):
                    data_pts[i,0] = c[i,0,0]
                    data_pts[i,1] = c[i,0,1]
                        
                # perform PCA analysis
                mean = np.empty((0))
                mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean)
                    
                # store and visualize the center of the object
                cntr = (int(mean[0,0]), int(mean[0,1]))
                cv2.circle(result_image, cntr, 3, (255, 0, 255), 2)
                
                # draw axes
                try:
                    # get endpoints of the object's axis
                    p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
                    p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
                except:
                    pass
                drawAxis(result_image, cntr, p1, (0, 255, 0), 0.1)
                drawAxis(result_image, cntr, p2, (255, 255, 0), 0.5)
            
            # draw box
            tl = round(0.002 * max(result_image.shape[0:2])) + 1  # line thickness
            c1, c2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
            cv2.rectangle(result_image, c1, c2, color, thickness=tl)
        
            # draw text
            display_txt = "%s: %.1f%%" % (coco_names[label], 100*score)
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(display_txt, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(result_image, c1, c2, color, -1)  # filled
            cv2.putText(result_image, display_txt, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
            
    # display the resulting image in a new window with title "Result"
    cv2.imshow("Result", result_image)

    # wait for key event
    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
        
# release video stream and close all windows
stream.release()
cv2.destroyAllWindows()