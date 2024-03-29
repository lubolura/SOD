#!/usr/bin/env python3

import time
import numpy as np
import cv2
import sod_utils
import sod_emails
import sod_camera_utils


def handle_actual_classes(st,cam,detected_classes,remove_classes):

    if (st.delay_to_ignore_same_class_detectection == 0):
        return

    # all classes we should detect
    for _class in cam["detect_classes"]:

        # we remove actual detected class, if there actually is
        if remove_classes:
            cam["detections"] = 0
            if (_class in detected_classes) and (_class in cam["detect_classes_actual"]):
                cam["detect_classes_actual"].remove(_class)
                cam["classes_timeouts"][_class] = time.time()
                sod_utils.debug(f"Class '{_class}' was removed from actuals. Actuals : {cam['detect_classes_actual']}", "stdout")

        # return class back if timeout is satified
        if _class not in cam["detect_classes_actual"]:
            if (time.time() - cam["classes_timeouts"].get(_class,
                                                          time.time())) > st.delay_to_ignore_same_class_detectection:
                cam["detect_classes_actual"].append(_class)
                cam["classes_timeouts"][_class]= time.time()
                sod_utils.debug(f"Class '{_class}' was added to actuals. Actuals : {cam['detect_classes_actual']}", "stdout")


def  set_camera_state(st,cam,frame):
        #count_to_fire_send_emails_when_camera_lost = st.count_to_fire_send_emails_when_camera_lost
        #send_emails_when_camera_lost =  st.send_emails_when_camera_lost
        # just remember if camnera is ok - or send email if not
        if (frame is None):
            if (cam["camera_is_ok"] == True):
                if (st.count_to_fire_send_emails_when_camera_lost == 0) or (cam["count_to_fire_send_emails_when_camera_lost"] >= st.count_to_fire_send_emails_when_camera_lost):
                    cam["camera_is_ok"] = False   # out of operation
                    sod_utils.debug(f"Camera  {cam['name']} is lost.", "stderr")
                    if st.send_emails_when_camera_lost:
                        msg = f"Camera signal {cam['name']} is lost."
                        subj = f"{sod_utils.get_time()} : {cam['name']} : is lost."
                        if not sod_emails.send_emails(st, subj, msg, None):
                            sod_utils.debug(f"Cannot send email."+msg , "stderr")
                else:
                    cam["count_to_fire_send_emails_when_camera_lost"] = cam["count_to_fire_send_emails_when_camera_lost"] + 1
                    sod_utils.debug(f"Camera {cam['name']} is lost - counter : {cam['count_to_fire_send_emails_when_camera_lost']}","stdout")
            return False

        # we have valid picture frame camera
        if (cam["camera_is_ok"] == False):
            cam["count_to_fire_send_emails_when_camera_lost"] = 0
            cam["camera_is_ok"] = True  # return back to operation
            sod_utils.debug(f"Camera  {cam['name']} is online.", "stdout")
            if st.send_emails_when_camera_lost:
                msg = f"Camera {cam['name']} is on. Actuals : {cam['detect_classes_actual']}"
                subj = f"{sod_utils.get_time()} : {cam['name']} : is on."
                if not sod_emails.send_emails(st, subj, msg, None):
                    sod_utils.debug(f"Cannot send email."+msg, "stderr")

        return True


def handle_positive_emails(st,email_subj, email_body, cam, out_img):
    # retunrn True if we have satisfied count and we can remove class from detections
    if st.detections_to_fire_delay_between_emails > 0:
        # we do not check delays if thi sis requested by setup
        # and still not enough detections
        if cam["detections"] < st.detections_to_fire_delay_between_emails:
            if sod_emails.send_emails(st, email_subj,email_body, out_img):
                cam["last_sent_email_time"] = time.time()
                # continue to detect and send emails
                cam["detections"] = cam["detections"] + 1
                sod_utils.debug(f"Detections (1) cam[detections] : {cam['detections']}", "stdout")
                return False

    # dont requested by setup or enough detections in one row
    try:
        if (time.time() - cam["last_sent_email_time"] >= st.delay_between_emails_secs):
                # go !
                if sod_emails.send_emails(st,email_subj, email_body, out_img):
                    cam["last_sent_email_time"] = time.time()
                cam["detections"] = cam["detections"] + 1
                sod_utils.debug(f"Detections (2) cam[detections] : {cam['detections']}", "stdout")
                return False
        else:
            sod_utils.debug(f"Skipping detection (delay_between_emails_secs).", "stdout")
    except Exception as e:
            sod_utils.debug(f"Error (1) during (delay_between_emails_secs) function : {e}", "stderr")
            return False
    #emails detections are satisfied, remove class from detection
    return True

#web_frame = {}

def mark_camera_error(cam):
    if isinstance(cam.get("farme_with_detections_and_regions", None),(np.ndarray)):
        cam["farme_with_detections_and_regions_for_web"] = cam["farme_with_detections_and_regions"].copy()
        text = f"LOST SIGNAL (errs: {cam['camera_err_cnt']}) "
        cv2.putText(
            cam["farme_with_detections_and_regions_for_web"], text, (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,255, 204) , 1
        )
        #print(text)


def mark_camera_ok(cam):
    if isinstance(cam.get("resized_frame", None),(np.ndarray)):
        text = f"{cam['frame_datetime']}"
        cv2.putText(
            cam["resized_frame"], text, (30, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (0, 255,  0), 1
        )



def guard(st,detector,should_by_showed):

    for cam in st.cams:

        if cam["camera_is_ok"] == False:
            sod_camera_utils.init_camera(cam)

        if cam["cap"] is not None:
            frame = sod_camera_utils.get_sample_frame(cam["cap"])


            if not set_camera_state(st,cam, frame):
                # camera is out of order
                sod_camera_utils.soft_init_camera(cam)
                cam["camera_err_cnt"] = cam["camera_err_cnt"] + 1
                mark_camera_error(cam)
            else:
                # resize - to process same size as regions definitions are
                frame = cv2.resize(frame, st.processing_picture_size)
                #unmasked_frame[cam["name"]] = frame.copy()
                cam["resized_frame"] = frame
                cam["frame_datetime"] = sod_utils.get_time()
                cam["camera_err_cnt"] = 0
                mark_camera_ok(cam)

                # frame is ok, camera is ok, lets detect
                detected_classes = []
                remove_classes = False
                if len(cam["detect_classes_actual"]) > 0:

                    # request to detect someting
                    detected_classes,frame_with_detections, farme_with_detections_and_regions = detector.Detect(cam = cam)

                    if len(detected_classes) > 0 :
                        if cam["guard_state"]:
                            # time for email ?
                            msg = f"Detected : {detected_classes}"
                            sod_utils.debug(msg, "stdout")
                            subj = f" {sod_utils.get_time()} : {cam['name']} detected class."
                            remove_classes = handle_positive_emails(st, subj, msg, cam, frame_with_detections)

                    cam["farme_with_detections_and_regions"] = farme_with_detections_and_regions
                    cam["farme_with_detections_and_regions_for_web"] = farme_with_detections_and_regions.copy()

                # filter do not detect/send same calssses repeatly within certain time
                handle_actual_classes(st, cam, detected_classes, remove_classes)

    #show all images as one big
    if should_by_showed:
        final_frame = None
        for cam in st.cams:
            if (not isinstance(cam["farme_with_detections_and_regions"],(np.ndarray))):
                continue

            if (not isinstance(final_frame,(np.ndarray))) :
                final_frame =cam["farme_with_detections_and_regions"]
                continue

            final_frame = np.hstack((final_frame, cam["farme_with_detections_and_regions"]))

        if (isinstance(final_frame,(np.ndarray))):
            cv2.imshow("Analyzed picture", final_frame)
            return True

    return False
