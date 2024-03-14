#!/usr/bin/env python3

# code is based on example here:
# https://korlakuntasaikamal10.medium.com/yolov4-a-comprehensive-guide-to-object-detection-using-darknet-and-opencv-bcf1688f57d7
# and
# https://github.com/erentknn/yolov4-object-detection


from ultralytics import YOLO
import cv2
import os
import numpy as np
import time
import sod_utils



class Yolo:
    def __init__(self,st,color = (255, 0, 0)):
        self.weights = st.darknet_weights  # loading weights
        self.cfg = st.darknet_config  # loading cfg file
        self.detector = 'yolov8'
        self.init_yolov4(st)
        self.init_yolov8(st)
        self.color = color
        if not os.path.isfile(st.darknet_classes):
            sod_utils.debug("Unable to open {:s}.\n".format(st.darknet_classes),"stderr")
            self.classes = []
        else:
            with open(st.darknet_classes, 'r') as f:
                self.classes = f.read().splitlines()


    def init_yolov4(self,st):
        self.yolov4 = cv2.dnn.readNetFromDarknet(self.cfg, self.weights)
        self.outputs = self.yolov4.getUnconnectedOutLayersNames()
        self.yolov4_size = st.darknet_size

    def init_yolov8(self,st):
        self.yolov8 = YOLO("yolov8n.pt")



    def Detect(self,cam):
        try:
            regions = cam["regions"]
            # do it with black-out masks
            masked_image = self.mask_regions(cam["resized_frame"].copy(),regions,(0,0,0),1)

            if self.detector == 'yolov8':
                yolov8_detections = self.yolov8.predict(masked_image)
                if len(yolov8_detections[0].boxes) > 0 :
                    frame_with_detection,detected_classes = self.process_detections(yolov8_detections, cam["resized_frame"],
                                                                                       cam["detect_classes_actual"],
                                                                                       cam["confidence_threshold"])
            else:
                blob = cv2.dnn.blobFromImage(masked_image, 1 / 255, (self.yolov4_size, self.yolov4_size), True, crop=False)
                self.yolov4.setInput(blob)
                yolov4_detections = self.yolov4.forward(self.outputs)
                frame_with_detection,detected_classes = self.process_detections(yolov4_detections, cam["resized_frame"],
                                                                                       cam["detect_classes_actual"],
                                                                                       cam["confidence_threshold"])

            frame_with_detections_and_regions = self.mask_regions(frame_with_detection,regions,(100,100,100),0.25)
            return detected_classes, frame_with_detection,frame_with_detections_and_regions

        except Exception as e:
            print(f'Error in : {e}')
            return set(),None,None

    def mark_results(self, image, boxes,confidences,class_ids):
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.01, 0.4)
        if len(idxs) > 0:
            for i in idxs.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                cv2.rectangle(image, (x, y), (x + w, y + h), self.color, 1)
                text = "{}: {:.4f}".format(self.classes[class_ids[i]], confidences[i])
                cv2.putText(
                    image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color, 1
                )
        return image

    def mask_regions(self, frame, regions, color, alpha):
        out_frame = frame.copy()
        frame_cpy = frame.copy()
        for reg in regions:
            (x, y) = int(reg["x"]), int(reg["y"])
            (w, h) = int(reg["w"]), int(reg["h"])
            cv2.rectangle(out_frame, (x, y), (x + w, y + h), color, cv2.FILLED)

        out_frame = cv2.addWeighted(out_frame, alpha, frame_cpy, 1 - alpha, gamma=0)
        return out_frame


    def process_detections(self, detections, input_frame, detect_classes, confidence_threshold):
        out_frame = input_frame.copy()
        (H, W) = out_frame.shape[:2]
        boxes = list()
        confidences = list()
        class_ids = list()
        classes = list()
        if self.detector == 'yolov4':
            _detections = []
            for _det in detections:
                for __det in _det:
                 _detections.append(__det)
        else:
            _detections = detections[0].boxes.data

        for det in _detections:

            if self.detector == 'yolov4':
                _scores = det[5:]
                class_id = np.argmax(_scores)
                confidence = _scores[class_id]
            else:
                confidence, class_id = map(float, det[4:6].tolist())
                class_id = int(class_id)

            # filter for desired classes only
            if self.classes[class_id] not in detect_classes:
                continue

            # filter for confidence threshold
            if confidence > confidence_threshold:
                if self.detector == 'yolov4':
                    box = det[0:4] * np.array([W, H, W, H])
                    (center_x, center_y, width, height) = box.astype("int")
                    xmin = int(center_x - (width / 2))
                    ymin = int(center_y - (height / 2))
                else:
                    xmin, ymin, xmax, ymax = map(int, det[:4].tolist())
                    width = xmax - xmin
                    height = ymax - ymin

                boxes.append([xmin, ymin, width,height])
                confidences.append(float(confidence))
                class_ids.append(class_id)
                classes.append(self.classes[class_id])

        if len(classes) > 0:
            out_frame = self.mark_results(out_frame, boxes, confidences, class_ids)
        return out_frame, set(classes)




    def process_yolov4_detections(self, model_type,layer_outs, input_frame, detect_classes, confidence_threshold):
        out_frame = input_frame.copy()
        (H, W) = out_frame.shape[:2]
        boxes = list()
        confidences = list()
        class_ids = list()
        classes = list()

        for output in layer_outs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # filter for desired classes only
                if self.classes[class_id] not in detect_classes:
                    continue

                # filter for confidence threshold
                if confidence > confidence_threshold:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (center_x, center_y, width, height) = box.astype("int")

                    x = int(center_x - (width / 2))
                    y = int(center_y - (height / 2))

                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                    classes.append(self.classes[class_id])

        if len(classes) > 0 :
            out_frame = self.mark_results(out_frame, boxes,confidences,class_ids)
        return out_frame,set(classes)


