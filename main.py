import sensor, image, time,math,pyb
from pyb import UART,LED
import json,network
import ustruct
import struct

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)#320*240
sensor.skip_frames(time=20)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_hmirror(True)
sensor.set_vflip(True)
clock = time.clock()

def auto_get_colour():#自适应阈值
# Capture the color thresholds for whatever was in the center of the image.
    r = [(320//2)-(50//2), (240//2)-(50//2), 40, 40] # 50x50 center of QVGA.

    print("Auto algorithms done. Hold the object you want to track in front of the camera in the box.")
    print("MAKE SURE THE COLOR OF THE OBJECT YOU WANT TO TRACK IS FULLY ENCLOSED BY THE BOX!")
    #LED(1).on()
    #time.sleep(500)
    #LED(1).off()
    #time.sleep(500)
    #LED(1).on()
    #time.sleep(500)
    #LED(1).off()
    #time.sleep(500)
    #LED(1).on()
    #time.sleep(500)
    #LED(1).off()
    #time.sleep(500)

    for i in range(100):
        img = sensor.snapshot()
        img.draw_rectangle(r)

    print("Learning thresholds...")
    threshold = [40, 40, 0, 0, 0, 0] # Middle L, A, B values.
    for i in range(100):
        img = sensor.snapshot()
        hist = img.get_histogram(roi=r)
        lo = hist.get_percentile(0.01) # Get the CDF of the histogram at the 1% range (ADJUST AS NECESSARY)!
        hi = hist.get_percentile(0.99) # Get the CDF of the histogram at the 99% range (ADJUST AS NECESSARY)!
        # Average in percentile values.
        threshold[0] = (threshold[0] + lo.l_value()) // 2
        threshold[1] = (threshold[1] + hi.l_value()) // 2
        threshold[2] = (threshold[2] + lo.a_value()) // 2
        threshold[3] = (threshold[3] + hi.a_value()) // 2
        threshold[4] = (threshold[4] + lo.b_value()) // 2
        threshold[5] = (threshold[5] + hi.b_value()) // 2
        for blob in img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=10):
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_rectangle(r)

    print("Thresholds learned...")
    print("Tracking colors...")
    #LED(3).on()
    #time.sleep(500)
    #LED(3).off()
    #time.sleep(500)
    #LED(3).on()
    #time.sleep(500)
    #LED(3).off()
    #time.sleep(500)
    #LED(3).on()
    #time.sleep(500)
    #LED(3).off()
    #time.sleep(500)
    return threshold

black_threshold =auto_get_colour()

uart = UART(3,115200)   #定义串口3变量
uart.init(115200, bits=8, parity=None, stop=1) # init with given parameters

#ROI_Index=0
ROI=[(0,160,320,80),(0,80,320,80),(0,0,320,80)]

def find_max(blobs):    #定义寻找色块面积最大的函数
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    cx = cy = cw = ch = 0
    uart.write(bytes([0x2C,0x12]))
    for ROI_Index in range(len(ROI)):
        blobs = img.find_blobs([black_threshold],roi=ROI[ROI_Index]
        ,invert=False,area_threshold=500,pixels_threshold=500)
    #第一个模块
        #uart.write(bytes([0x2C,0x12]))
        if blobs:
            max_b = find_max(blobs)
            cx=max_b[5]
            cy=max_b[6]
            cw=max_b[2]
            ch=max_b[3]
            img.draw_rectangle(max_b[0:4],color=(0,0,255))
            img.draw_cross(max_b[5], max_b[6])

            if 0 < cx < 100:
                uart.write(bytes([0x01]))
            elif 110 < cx < 210:
                uart.write(bytes([0x02]))
            elif 220 < cx < 320:
                uart.write(bytes([0x03]))
            print(cx,cy,cw,ch)
        else:
            uart.write(bytes([0x00]))

        #time.sleep_ms(500)
    #checksum=sum(int(cx))
    #uart.write(bytes([checksum]))
    uart.write(bytes([0x5B]))
    print(black_threshold)
