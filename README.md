# SOD
simple Stream Object Detection using yolov4 , 
inspired by https://github.com/montagdude/zoneminder-notifier

The program is created in python. Actively uses YOLOV4 object detection. 

Yolo4 itself is not part of the distribution. The pre-trained model is freely accessible and you have to download it:

https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights
https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.cfg

and save in the following directories:

model_path: /usr/share/sod/yolov4/yolov4.weights

config_path: /usr/share/sod/yolov4/yolov4.cfg

classes_path: /usr/share/sod/coco.names.80

in the case of using the yolov8 model:
for n model:
https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt"
model_yolov8_path: /usr/share/sod/yolov8/yolov8n.pt
or possibly s, m, l model models - see config


. It is also necessary to have Python3 installed with the required libraries.
If the yolov8 model is also used - it is an ultralytics module


Before installation, it is necessary to configure/edit the file

sod.cfg 

and set the individual items correctly - see the comments in the sod.cfg file.

Also make sure that the mail server is available.

The program itself is installed on Ubuntu by command

python3 setup.py install

whereby it is necessary to install from the addresary in which the source codes themselves are.

Next, it is possible to check whether the process is running, for example:

systemctl status sod

In case of problems, check the relevant log files - see their definitions in sod.cfg.


----------------------------------------------------------------------------------------

Program je vytvoreny v jazyu python. Aktivne pouziva YOLOV4 detekciu objektov. Samotny yolo4 nie je sucastou distribucie. Natrenovany model je volne pristupny a musis si ho stiahnut :

https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights
https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.cfg

a ulozit do nasledovnych adresarov :

model_path: /usr/share/sod/yolov4/yolov4.weights

config_path: /usr/share/sod/yolov4/yolov4.cfg

classes_path: /usr/share/sod/coco.names.80

v pripade pouzitia modelu yolov8 :
pre n model :
https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt"
model_yolov8_path: /usr/share/sod/yolov8/yolov8n.pt
alebo popripade s,m,l verie modelov modely - vid config


. Taktiez je potrebne mat nainstalovany Python s pozadovanymi kniznicami.
V pripade ze sa pouzije aj model yolov8 - je to modul ultralytics

Pred instalaciou je potrebne nakonfigurovat/zeditovat subor 
sod.cfg a spravne nastavit jednotlive polozky - vid komentar v subore sod.cfg. 

Tiez sa uzbezpec ze je mailovy server dostupny.

Samotny program sa na linuxe instaluje povelom 

python3 setup.py install

pricom je potrebne instalovat z adresara v ktorom su samotne zdrojove kody .

Nasledne je mozne skontrolovat ci je proces spusteny, napr : 

systemctl status  sod

V pripade vyskytu problemov skonttrolovat prislusne log fajly - vid ich definicie v sod.cfg.