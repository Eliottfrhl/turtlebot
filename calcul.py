import time
from xml.etree.ElementTree import tostring
import zenoh
import argparse
import imutils
import io
import cv2
import json
import random
import binascii
import numpy as np
import sys
from datetime import datetime
from pycdr import cdr
from pycdr.types import int8, int32, uint32, float64


@cdr
class Vector3:
    x: float64
    y: float64
    z: float64


@cdr
class Twist:
    linear: Vector3
    angular: Vector3


@cdr
class Time:
    sec: int32
    nanosec: uint32


@cdr
class Log:
    stamp: Time
    level: int8
    name: str
    msg: str
    file: str
    function: str
    line: uint32


parser = argparse.ArgumentParser(
    prog='calcul',
    description='calcul de la commande en fonction de la box')
parser.add_argument('-m', '--mode', type=str, choices=['peer', 'client'],
                    help='The zenoh session mode.')
parser.add_argument('-e', '--connect', type=str, metavar='ENDPOINT', action='append',
                    help='zenoh endpoints to connect to.')
parser.add_argument('-l', '--listen', type=str, metavar='ENDPOINT', action='append',
                    help='zenoh endpoints to listen on.')
parser.add_argument('-i', '--id', type=int, default=random.randint(1, 999),
                    help='The Camera ID.')
parser.add_argument('-w', '--width', type=int, default=200,
                    help='width of the published faces')
parser.add_argument('-q', '--quality', type=int, default=95,
                    help='quality of the published faces (0 - 100)')
parser.add_argument('-a', '--cascade', type=str,
                    default='haarcascade_frontalface_default.xml',
                    help='path to the face cascade file')
parser.add_argument('-d', '--delay', type=float, default=0.05,
                    help='delay between each frame in seconds')
parser.add_argument('-p', '--prefix', type=str, default='/demo/facerecog',
                    help='resources prefix')
parser.add_argument('-c', '--config', type=str, metavar='FILE',
                    help='A zenoh configuration file.')
parser.add_argument('--cmd_vel', dest='cmd_vel',
                    default='/rt/turtle1/cmd_vel',
                    type=str,
                    help='The "cmd_vel" ROS2 topic.')

args = parser.parse_args()
conf = zenoh.config_from_file(
    args.config) if args.config is not None else zenoh.Config()
if args.mode is not None:
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))

#	initiate	logging
print('[INFO] Open zenoh session...')
zenoh.init_logger()

#	open	a	zenoh	session
z = zenoh.open(conf)


def callback1(sample):
    bit = sample.payload.decode('utf-8')
    valstr = str(bit)
    global cmd
    cmd = valstr


def callback2(sample):
    dict = json.loads(sample)
    print(dict['top'])


key_expr_sub_val = "/demo/boxes"
key_expr_sub_box = '{}/faces/{}/{}/box/**'
key_exp_pub = args.cmd_vel
#	subscribe
print('[INFO] Start detection')
sub1 = z.subscribe(key_expr_sub_val, callback1)
sub2 = z.subscribe(key_expr_sub_box, callback2)


def pub_twist(linear, angular):
    print("Pub twist: {} - {}".format(linear, angular))
    t = Twist(linear=Vector3(x=linear, y=0.0, z=0.0),
              angular=Vector3(x=0.0, y=0.0, z=angular))
    z.put(key_exp_pub, t.serialize())


while True:
    time.sleep(1.0)
    print(cmd)
    if cmd == '1':
        print("J'avance")
        #pub_twist(20, 0)
    elif cmd == "0":
        print("Je tourne")
        #pub_twist(0, 20)
