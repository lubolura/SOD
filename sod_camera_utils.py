import time
import cv2
import sod_utils
import threading

class VideoCapture:
    def __init__(self, cam):
        try:
            self.cap = cv2.VideoCapture(cam["stream"])
            self.lock = threading.Lock()
            self.t = threading.Thread(target=self._reader,name = cam["name"])
            self.t.daemon = True
            self.t.start()
            self.init_ok = True
            self.grab_ok = False
            sod_utils.debug(f"Deamon for camera {cam['name']} init ok.", "stdout")
        except Exception as e:
            sod_utils.debug(f"Deamon for camera {cam['name']} init Err : {e}", "stderr")
            self.init_ok = False

    # grab frames as soon as they are available
    def _reader(self):
        while True:
            with self.lock:
                ret = self.cap.grab()
            if ret:
                self.grab_ok = True
            else:
                break
        time.sleep(1/100)

    # retrieve latest frame
    def read(self):
        with self.lock:
            if self.grab_ok:
                _, frame = self.cap.retrieve()
                self.grab_ok = False
                return frame
            else:
                return None


def get_sample_frame(cap):
    if cap is not None:
        try:
            #ret, frame = cap.read()
            frame = cap.read()
            return frame
        except Exception as e:
            sod_utils.debug(f"Cannot read camera : {e}", "stderr")
    return None

def soft_init_camera(cam):
        #cap = VideoCapture(cam["stream"])
        cap = VideoCapture(cam)
        if isinstance(cap, VideoCapture):
            if cap.init_ok :
                sod_utils.debug(f"Camera {cam['name']} SOFT init", "stdout")
                return cap
        sod_utils.debug(f"Cannot SOFT init camera ", "stderr")
        return None

def init_camera(cam):
    cam["cap"] = soft_init_camera(cam)
    if isinstance(cam["cap"],VideoCapture):
        cam["detect_classes_actual"] = cam["detect_classes"].copy()
        cam["classes_timeouts"] = {_class: time.time() for _class in cam["detect_classes"]}
        sod_utils.debug(f"Camera {cam['name']} init", "stdout")
    else:
        sod_utils.debug(f"Cannot init camera {cam['name']}", "stderr")
        cam["cap"] = None
        cam["detect_classes_actual"] = []
        cam["classes_timeouts"] = {}
    cam["last_sent_email_time"] = None
    cam["camera_is_ok"] = False
    cam["detections"] = 0
    sod_utils.debug(f"Camera {cam['name']} - Actuals : {cam['detect_classes_actual']}", "stdout")



def init_camera_definitions(st):
    for cam in st.cams:
        cam["cap"] = None
        cam["last_sent_email_time"] = None
        cam["detect_classes_actual"] = []
        cam["classes_timeouts"] = {}
        cam["camera_is_ok"] = False
        cam["camera_err_cnt"] = 0
        cam["detections"] = 0
        cam["count_to_fire_send_emails_when_camera_lost"] = 0
        cam["frame_datetime"] = "-"
        cam["farme_with_detections_and_regions"] = None
        cam["farme_with_detections_and_regions_for_web"] = None

def release_cameras(st):
    for cam in st.cams:
        if cam["cap"] is not None:
            #cam["cap"].release()
            #cam["cap"] = None
            pass
