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

black_threshold =(0, 30, -18, 8, -13, 3)

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
        blobs = img.find_blobs([black_threshold],roi=ROI[ROI_Index],invert=False,area_threshold=500,pixels_threshold=500)
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

            if 10 < cx < 70:
                uart.write(bytes([0x01]))
            elif 70 < cx < 130:
                uart.write(bytes([0x02]))
            elif 130 < cx < 190:
                uart.write(bytes([0x03]))
            elif 190 < cx < 250:
                uart.write(bytes([0x04]))
            elif 250 < cx < 310:
                uart.write(bytes([0x05]))
            print(cx,cy,cw,ch)
        else:
            uart.write(bytes([0x00]))

        time.sleep_ms(500)
    #checksum=sum(int(cx))
    #uart.write(bytes([checksum]))
    uart.write(bytes([0x5B]))
