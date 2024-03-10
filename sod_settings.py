#!/usr/bin/env python3

import configparser
import os
import sys
import shutil
import json
import sod_utils

CONFIG_SYS_SECTIONS = ["General","Darknet","WebClient"]

class Settings:
    def __init__(self, config_file="/etc/sod.cfg"):
        self.config_file = config_file
        config = configparser.ConfigParser()
        try:
            f = open(self.config_file)
        except IOError:
            sod_utils.debug("Error opening {:s}".format(self.config_file), "stderr")
            sys.exit(1)
        f.close()
        if len(config.read(self.config_file)) == 0:
            sod_utils.debug("Error parsing {:s}".format(self.config_file), "stderr")
            sys.exit(1)

        for section in CONFIG_SYS_SECTIONS:
            if not config.has_section(section):
                sod_utils.debug("No section {} found in {}".format(section, self.config_file),
                              "stderr")
                sys.exit(1)

        # just rounds counter
        self.rounds = 0

        section = "General"
        self.debug_logs = sod_utils.get_int_from_config(config, section, "debug_logs",
                                                            required=False, default=0)
        self.delay_between_samples_secs = sod_utils.get_int_from_config(config, section, "delay_between_samples_secs",
                                                            required=False, default=2)
        self.detections_to_fire_delay_between_emails = sod_utils.get_int_from_config(config, section, "detections_to_fire_delay_between_emails",
                                                            required=False, default=2)
        self.delay_between_emails_secs = sod_utils.get_int_from_config(config, section, "delay_between_emails_secs",
                                                            required=False, default=180)
        self.delay_to_ignore_same_class_detectection = sod_utils.get_int_from_config(config, section, "delay_to_ignore_same_class_detectection",
                                                            required=False, default=180)
        self.email_addresses = sod_utils.get_from_config(config, section, "email_addresses", required=False,
                                                         default = "")
        self.email_client = sod_utils.get_from_config(config, section, "email_client", required=False,
                                                         default = "smtp")
        self.smtp_server = sod_utils.get_from_config(config, section, "smtp_server", required=False,
                                                         default = "")
        self.smtp_usr = sod_utils.get_from_config(config, section, "smtp_usr", required=False,
                                                         default = "")
        self.smtp_pwd = sod_utils.get_from_config(config, section, "smtp_pwd", required=False,
                                                         default = "")
        self.detect_classes = sod_utils.get_from_config(config, section, "email_addresses", required=False,
                                                         default = "")
        self.show_image = sod_utils.get_bool_from_config(config, section, "show_image",
                                                    required=False, default=True)

        self.send_emails_when_camera_lost = sod_utils.get_bool_from_config(config, section, "send_emails_when_camera_lost",
                                                    required=False, default=True)
        self.count_to_fire_send_emails_when_camera_lost = sod_utils.get_int_from_config(config, section, "count_to_fire_send_emails_when_camera_lost",
                                                    required=False, default=2)

        self.smtp_debug_log = sod_utils.get_bool_from_config(config, section, "smtp_debug_log",
                                                    required=False, default=False)

        processing_picture_size = sod_utils.get_from_config(config, section, "processing_picture_size", required=False, default="600,400")
        self.processing_picture_size = [int(x) for x in processing_picture_size.split(',')]


        section = "WebClient"
        self.cameras_in_row = sod_utils.get_int_from_config(config, section, "cameras_in_row",required=False, default=1)


        section = "Darknet"
        self.darknet_weights = os.path.join("/usr", "share", "sod", "yolov4","yolov4.weights")
        self.darknet_config = os.path.join("/usr", "share", "sod", "yolov4", "yolov4.cfg")
        self.darknet_classes = os.path.join("/usr", "share", "sod", "coco.names.80")
        self.darknet_size = sod_utils.get_int_from_config(config, section, "darknet_size",required=False, default=416)
        cam_def_sections = list(set(config.sections()) - set(CONFIG_SYS_SECTIONS))


        self.cams = []
        for section in cam_def_sections:
            cam = {}
            cam["name"] = section
            stream = sod_utils.get_from_config(config, section, "stream_source", required=True)
            if stream.isnumeric():
                stream = int(stream)
            cam["stream"] = stream
            detect_classes = sod_utils.get_from_config(config, section, "detect_classes", required=False, default="person")
            cam["detect_classes"] = detect_classes.split(',')
            cam["confidence_threshold"] = sod_utils.get_float_from_config(config, section, "confidence_threshold",
                                                            required=False, default=0.5)

            cam["regions"] = sod_utils.get_list_of_dicts_from_config(config, section, "regions",
                                                            required=False, default='[]')

            self.cams.append(cam)


    def store_cfg(self,camera_name,regions):
        # Read into memory
        config = configparser.ConfigParser()
        with open(self.config_file) as f:
            config.read_file(f)
        # Update the in-memory configuration
        config[camera_name]["regions"] = json.dumps(regions)
        try:
            with open(self.config_file+'.tmp', "w") as f:
                config.write(f)
            shutil.move(self.config_file, self.config_file+f'_bak_{sod_utils.get_time().replace(" ","_").replace(":","").replace(".","")}')
            shutil.copy2(self.config_file + '.tmp', self.config_file)
            return True
        except Exception as e:
            sod_utils.debug(f"{e}","stderr")
        return False


st = None