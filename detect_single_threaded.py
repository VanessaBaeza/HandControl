from utils import detector_utils as detector_utils
from predict import predict
import cv2
import tensorflow as tf
import numpy as np
import datetime
import argparse
import time
from tkinter import *
from PIL import Image, ImageTk
import sys
import pychromecast
import os
import os.path
from gtts import gTTS
import time
import hashlib
import sys
import pychromecast
# use for setting: ./ghome_volume [ghome_ip] [volume_from_0_to_100]
# use for reading: ./ghome_volume [ghome_ip]

#************
# Turn on/off the ability to save images, or control Philips Hue/Sonos
save_images, selected_gesture = False, 'peace'
smart_home = True

#Philips Hue Settings
bridge_ip = '192.168.0.103'
b = Bridge(bridge_ip)
on_command = {'transitiontime': 0, 'on': True, 'bri': 254}
off_command = {'transitiontime': 0, 'on': False, 'bri': 254}

#*************
detection_graph, sess = detector_utils.load_inference_graph()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-sth',
        '--scorethreshold',
        dest='score_thresh',
        type=float,
        default=0.2,
        help='Score threshold for displaying bounding boxes')
    parser.add_argument(
        '-fps',
        '--fps',
        dest='fps',
        type=int,
        default=1,
        help='Show FPS on detection/display visualization')
    parser.add_argument(
        '-src',
        '--source',
        dest='video_source',
        default=0,
        help='Device index of the camera.')
    parser.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=320,
        help='Width of the frames in the video stream.')
    parser.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=180,
        help='Height of the frames in the video stream.')
    parser.add_argument(
        '-ds',
        '--display',
        dest='display',
        type=int,
        default=1,
        help='Display the detected images using OpenCV. This reduces FPS')
    parser.add_argument(
        '-num-w',
        '--num-workers',
        dest='num_workers',
        type=int,
        default=4,
        help='Number of workers.')
    parser.add_argument(
        '-q-size',
        '--queue-size',
        dest='queue_size',
        type=int,
        default=5,
        help='Size of the queue.')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    start_time = datetime.datetime.now()
    num_frames = 0
    im_width, im_height = (cap.get(3), cap.get(4))
    # max number of hands we want to detect/track
    num_hands_detect = 1

    ########################
    # parameters
    #threshold = 60  # binary threshold
    #blurValue = 11  # GaussianBlur parameter
    bgSubThreshold = 50
    learningRate = 0

    # variableslt
    isBgCaptured = 0  # bool, whether the background captured
    triggerSwitch = False  # if true, keyboard simulator works

    def remove_background(frame):
        fgmask = bgModel.apply(frame, learningRate=learningRate)
        kernel = np.ones((3, 3), np.uint8)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        res = cv2.bitwise_and(frame, frame, mask=fgmask)
        return res

    ###########################

    cv2.namedWindow('Single-Threaded Detection', cv2.WINDOW_NORMAL)

    #obtain current status of devices

    foco_det = pychromecast.Chromecast(li)
    alarma_det = pychromecast.Chromecast(al)
    aire_det = pychromecast.Chromecast(ac)
    musica_det = pychromecast.Chromecast(pi)

    bool left
    bool fist
    bool okay
    bool palm
    

    while True:

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        ret, image_np = cap.read()
        # image_np = cv2.flip(image_np, 1)
        try:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        except:
            print("Error converting to RGB")

        # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
        # while scores contains the confidence for each of these boxes.
        # Hint: If len(boxes) >     1 , you may assume you have found atleast one hand (within your score threshold)

        boxes, scores = detector_utils.detect_objects(image_np, detection_graph, sess) 

        #################
        # Run once background is captured
        if isBgCaptured == 1:
            img = remove_background(image_np)
            cv2.imshow('set_bkg',img)

            # draw bounding boxes on frame and capture frame to predic the sign
            detector_utils.draw_capture_box_on_image(num_hands_detect, args.score_thresh,
                                         scores, boxes, im_width, im_height,
                                         image_np,img)

            # Predict sign
            sign_predicted = predict('temporal_hand_frame.jpg')

            if sign_predicted == 0:
                print("pred: Left")
                left=not left
            elif sign_predicted == 1:
                print("pred: C")
                c = not c
            elif sign_predicted == 2:
                print("pred: Fist")
                fist = not fist
                alarma_set = fist
            elif sign_predicted == 3:
                print("pred: Okay")
                okay = not okay
            elif sign_predicted == 4:
                print("pred: Palm")
                palm = not palm
            elif sign_predicted == 5:
                print("pred: Peace")
                peace = not peace
           
            # Add prediction and action text to thresholded image
            cv2.putText(thresh, f"Prediction: {prediction} ({score}%)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
            cv2.putText(thresh, f"Action: {action}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))  # Draw the text

            #Comunicate command to smart hub
            ip = sys.argv[1];
            say = sys.argv[2];
            al = sys.argv[3];
            li = sys.argv[4];
            ac = sys.argv[5];

            #********* retrieve local ip of my google home hub
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip=s.getsockname()[0]
            s.close()
            #**********************

            fname=hashlib.md5(say.encode()).hexdigest()+".mp3"; #create md5 filename for caching
            #turn on lights
            if foco_set == 0 & left_det == 1:
                lightdevice = pychromecast.Chromecast(li)
                lightdevice.wait()
                on_command
            #turn off lights
            else if foco_set == 1 & left_det == 0:
                lightdevice = pychromecast.Chromecast(li)
                lightdevice.wait()
                off_command
            #turn alarm off
            else if alarma_set == 1 & fist_det == 0:
                alarmdevice = pychromecast.Chromecast(al)
                alarmdevice.wait()
                al_prec=alarmdevice.status.off
                alarmdevice.set(0.0) #set alarm off
            #turn on AC
            else if aire_set == 0 & okay_det == 1:
                airdevice = pychromecast.Chromecast(ac)
                airdevice.wait()
                ac_prec=airdevice.status.onoff
                airdevice.set(1.0) #set AC ON
            #turn off AC
            else if aire_set == 1 & okay_det == 0:
                airdevice = pychromecast.Chromecast.(ac)
                airdevice.wait()
                ac_prec=airdevice.status.onoff
                airdevice.set(0.0) #set AC off
            #turn up music
            else if musica_set == 0 & palm_det == 1:
                ip=sys.argv[1]
                castdevice = pychromecast.Chromecast(ip)
                castdevice.wait()
                vol_prec=castdevice.status.volume_level
                castdevice.set_volume(0.0) #set volume 0 for not hear the BEEEP
                try:
                   vol=sys.argv[2]; #vol up
                except:
                   pass

                castdevice = pychromecast.Chromecast(ip)
                castdevice.wait()

                if vol==-1 :
                   vol_prec=castdevice.status.volume_level
                   print(round(vol_prec*100))
                else :
                   castdevice.set_volume(float(vol)/100)
            #turn off music
            else if musica_set == 1 & palm_det == 0:
                ip=sys.argv[1]
                castdevice = pychromecast.Chromecast(ip)
                castdevice.wait()
                vol_prec=castdevice.status.volume_level
                castdevice.set_volume(0.0) #set volume 0 for not hear the BEEEP
                try:
                   vol=sys.argv[3]; #vol udown
                except:
                   pass

                castdevice = pychromecast.Chromecast(ip)
                castdevice.wait()

                if vol==-1 :
                   vol_prec=castdevice.status.volume_level
                   print(round(vol_prec*100))
                else :
                   castdevice.set_volume(float(vol)/100)

            castdevice = pychromecast.Chromecast(ip)
            castdevice.wait()
            vol_prec=castdevice.status.volume_level
            castdevice.set_volume(0.0) #set volume 0 for not hear the BEEEP

            try:
               os.mkdir("/var/www/html/mp3_cache/")
            except:
               pass

            if not os.path.isfile("/var/www/html/mp3_cache/"+fname):
               tts = gTTS(say,lang='it')
               tts.save("/var/www/html/mp3_cache/"+fname)

            mc = castdevice.media_controller
            mc.play_media("http://"+local_ip+"/mp3_cache/"+fname, "audio/mp3")

            mc.block_until_active()

            mc.pause() #prepare audio and pause...

            time.sleep(1)
            castdevice.set_volume(vol_prec) #setting volume to precedent value
            time.sleep(0.2)

            mc.play() #play the mp3

            while not mc.status.player_is_idle:
               time.sleep(0.5)

            mc.stop()

            castdevice.quit_app()

            #************************************
           
        ####################    


        # Calculate Frames per second (FPS)
        num_frames += 1 
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        fps = num_frames / elapsed_time


        if (args.display > 0):
            # Display FPS on frame
            if (args.fps > 0):
                detector_utils.draw_fps_on_image("FPS : " + str(int(fps)),
                                                 image_np)
                cv2.imshow('Single-Threaded Detection',cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
            ##########################
            if cv2.waitKey(25) & 0xFF == ord('b'):  # press 'b' to capture the background
                bgModel = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
                time.sleep(2)
                isBgCaptured = 1
                print('Background captured')
            
            if cv2.waitKey(25) & 0xFF == ord('r'):  # press 'r' to reset the background
                time.sleep(1)
                bgModel = None
                triggerSwitch = False
                isBgCaptured = 0
                print('Reset background')

            if cv2.waitKey(25) & 0xFF == ord('m'):  # press 'm' open menu
                print('Open Menu')
                class Window(Frame):
                    def __init__(self, master=None):
                        Frame.__init__(self, master)
                        self.master = master
                        self.pack(fill=BOTH, expand=1)

                        frame= LabelFrame(self)
                        frame.grid(row = 0, column = 0, columnspan = 3)
                        frame.config(width="1000", height="1000")
                        frame.config(background="white")
                        frame.pack(fill=BOTH, expand=1)


                        load = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/Casa.PNG")
                        render = ImageTk.PhotoImage(load)
                        img = Label(frame, image=render)
                        img.image = render
                        img.grid(row=0, column=0,columnspan=5,rowspan=8)
                        
                        Label(frame, text = 'Bienvenido',font= ("Arial",20)).grid(row = 0, column = 1)
                        Label(frame, text = 'Seleccione la seña a configurar:',font= ("Arial",16)).grid(row = 1, column = 1)
                        
                        load1 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/ManoL.png")
                        render1 = ImageTk.PhotoImage(load1)
                        img1 = Label(frame, image=render1)
                        img1.image = render1
                        img1.grid(row=2, column=0)

                        load2 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/ManoOk.png")
                        render2 = ImageTk.PhotoImage(load2)
                        img2 = Label(frame, image=render2)
                        img2.image = render2
                        img2.grid(row=2, column=2)
                        
                        load3 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/ManoPalma.png")
                        render3 = ImageTk.PhotoImage(load3)
                        img3 = Label(frame, image=render3)
                        img3.image = render3
                        img3.grid(row=4, column=0)

                        load4 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/ManoPaz.png")
                        render4 = ImageTk.PhotoImage(load4)
                        img4 = Label(frame, image=render4)
                        img4.image = render4
                        img4.grid(row=4, column=2)

                        load5 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/ManoPuno.png")
                        render5 = ImageTk.PhotoImage(load5)
                        img5 = Label(frame, image=render5)
                        img5.image = render5
                        img5.grid(row=6, column=1)

                        BotonL = Button(frame, text= "L", command = self.edit_sign).grid(row=3, column= 0,sticky= W + E)
                        BotonOk = Button(frame, text= "Ok", command = self.edit_sign).grid(row=3, column= 2,sticky= W + E)
                        BotonPalma = Button(frame, text= "Palma", command = self.edit_sign).grid(row=5, column= 0,sticky= W + E)
                        BotonPaz = Button(frame, text= "Paz", command = self.edit_sign).grid(row=5, column= 2,sticky= W + E)
                        BotonPuño = Button(frame, text= "Puño", command = self.edit_sign).grid(row=7, column= 1,sticky= W + E)

                    def edit_sign(self):
                        self.edit_wind = Toplevel()

                        frame1= LabelFrame(self.edit_wind)
                        frame1.grid(row = 0, column = 0)
                        frame1.config(width="1000", height="1000")
                        frame1.config(background="white")
                        frame1.pack(fill=BOTH, expand=1)

                        load11 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/Casa2.PNG")
                        render11 = ImageTk.PhotoImage(load11)
                        img11 = Label(frame1, image=render11)
                        img11.image = render11
                        img11.grid(row=0, column=0,columnspan=6,rowspan=9)
                       
                        Label(frame1, text = 'Seleccione acción a asignar:',font= ("Arial",16)).grid(row = 0, column = 1)

                        load6 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/Foco.png")
                        render6 = ImageTk.PhotoImage(load6)
                        img6 = Label(frame1, image=render6)
                        img6.image = render6
                        img6.grid(row=1, column=0)
                        
                        load7 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/Alarma.png")
                        render7 = ImageTk.PhotoImage(load7)
                        img7 = Label(frame1, image=render7)
                        img7.image = render7
                        img7.grid(row=1, column=2)
                        
                        load8 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/Aire.png")
                        render8 = ImageTk.PhotoImage(load8)
                        img8 = Label(frame1, image=render8)
                        img8.image = render8
                        img8.grid(row=3, column=0)
                       
                        load9 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/Musica.png")
                        render9 = ImageTk.PhotoImage(load9)
                        img9 = Label(frame1, image=render9)
                        img9.image = render9
                        img9.grid(row=3, column=2)
                        
                        load10 = Image.open("/home/vanessa/Documents/PIM/Manu_Ivan/Home.png")
                        render10 = ImageTk.PhotoImage(load10)
                        img10 = Label(frame1, image=render10)
                        img10.image = render10
                        img10.grid(row=5, column=1)
                        
                        BotonFoco = Button(frame1, text= "Foco On/Off").grid(row=2, column= 0,sticky= W + E)
                        BotonAlarma = Button(frame1, text= "Alarma On/Off").grid(row=2, column= 2,sticky= W + E)
                        BotonAire = Button(frame1, text= "Aire On/Off").grid(row=4, column= 0,sticky= W + E)
                        BotonMusica = Button(frame1, text= "Música On/Off").grid(row=4, column= 2,sticky= W + E)
                        BotonHome = Button(frame1, text= "Inicio", command = root.destroyAllWindows).grid(row=6, column= 1,sticky= W + E)

                      


                root = Tk()
                app = Window(root)
                root.wm_title("Hand-Control App")
                root.geometry("800x800")
                root.config(background="white")

                root.mainloop()
            ##############################
            
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

        else:
            print("frames processed: ", num_frames, "elapsed time: ",
                  elapsed_time, "fps: ", str(int(fps)))
