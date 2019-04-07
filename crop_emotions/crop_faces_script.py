# *******************************************************************
# Face detection using the YOLOv2-tiny algorithm + age and gender recognition
#
# Description : crop_faces_script.py
# The main code of the Face detection using the YOLOv3 algorithm
#
# *******************************************************************

# Usage example:  python crop_faces_script.py --image samples/outside_000001.jpg \
#                                    --output-dir outputs/
#                 python crop_faces_script.py --video samples/subway.mp4 \
#                                    --output-dir outputs/
#                 python crop_faces_script.py --src 1 --output-dir outputs/


import argparse
import random
import sys
import os

from utils import *
import numpy as np

#####################################################################
parser = argparse.ArgumentParser()

parser.add_argument('--model-cfg', type=str, default='/home/hikkav/crop_emotions/cfg/tiny_yolo.cfg',
                    help='path to config file')
parser.add_argument('--model-weights', type=str,
                    default='/home/hikkav/crop_emotions/cfg/yolov2-tiny-train-one-class_32600.weights',
                    help='path to weights of model')
parser.add_argument('--image', type=str, default='',
                    help='path to image file')
parser.add_argument('--video_dir', type=str, default=None,
                    help='path to video file')
parser.add_argument('--src', type=int, default=0,
                    help='source of the camera')
parser.add_argument('--output-dir', type=str, default='outputs/',
                    help='path to the output directory')
parser.add_argument('--skip', type=int, default=1,
                    help='how many frames to skip')
parser.add_argument('--shape', type=str, default='circle',
                    help='what shapes of bounding boxes are available')
parser.add_argument('--classes', type=str, default='/home/hikkav/crop_emotions/crop.names',
                    help='path to list with classes to predict')
args = parser.parse_args()

#####################################################################


# print the arguments
print('----- info -----')
print('[i] The config file: ', args.model_cfg)
print('[i] The weights of model file: ', args.model_weights)

print('###########################################################\n')

# Give the configuration and weight files for the model and load the network
# using them.


net = cv2.dnn.readNetFromDarknet(args.model_cfg, args.model_weights)

net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

counter = random.randint(0, 583213)
cropped = 0


#######################################################################
# my part of code

def get_classes():
    class_list = open(args.classes).read().strip().split('\n')
    return class_list


def make_dir():
    if not os.path.exists('cropped_dataset'):
        os.mkdir('cropped_dataset')
        print('Made dir')


def make_inputs(faces, frame):
    global counter
    global cropped
    inputs_lis = []

    crop_faces = [(faces[i][0], faces[i][1], faces[i][2] + faces[i][0], faces[i][3] + faces[i][1]) for i in
                  range(len(faces))]

    for i in range(len(crop_faces)):
        counter += 1
        img = Image.fromarray(np.asarray(frame)).crop(crop_faces[i]).convert('RGB')

        img.save('cropped_dataset/cropped_emotions.{}.png'.format(counter))

    return inputs_lis, crop_faces


def end_to_end(faces, frame):
    make_inputs(faces, frame)


####################################################################
def _main():
    make_dir()
    wind_name = 'cropping faces using tiny yolov2'
    cv2.namedWindow(wind_name, cv2.WINDOW_NORMAL)
    video_list = []
    output_file = ''
    class_list = get_classes()

    if args.video_dir is not None:
        if not os.path.exists(args.video_dir):
            print('The path {} does not exist '.format(args.video))
        for i in os.listdir(args.video_dir):
            if not os.path.isfile(args.video_dir + '/' + i):
                print("[!] ==> Input video file {} doesn't exist".format(args.video))
                sys.exit(1)
            video_list.append(args.video_dir + '/' + i)
    else:
        video_list.append(1)

    # Get the video writer initialized to save the output video

    for i in video_list:
        if i != 1:
            cap = cv2.VideoCapture(i)
        else:

            cap = cv2.VideoCapture(args.src)

        n = 0
        while True:

            has_frame, frame = cap.read()

            # Stop the program if reached end of video
            if not has_frame:
                print('[i] ==> Done processing!!!')
                print('[i] ==> Output file is stored at', os.path.join(args.output_dir, output_file))
                cv2.waitKey(1000)
                break
            if args.skip != n:
                n += 1
                continue
            n = 0

            # Create a 4D blob from a frame.

            blob = cv2.dnn.blobFromImage(frame, 1 / 255, (IMG_WIDTH, IMG_HEIGHT),
                                         [0, 0, 0], 1, crop=False)

            # Sets the input to the network
            net.setInput(blob)

            # Runs the forward pass to get output of the output layers

            outs = net.forward(get_outputs_names(net))

            # Remove the bounding boxes with low confidence
            people, ids, indices = post_process(frame, outs, CONF_THRESHOLD, NMS_THRESHOLD, args.shape, class_list,
                                                )

            end_to_end(people, frame)

            print('[i] ==> # detected  objects: {}'.format(len(people)))
            print('#' * 60)

            # initialize the set of information we'll displaying on the frame
            info = [
                ('number of objects detected', '{}'.format(len(people)))
            ]

            for (i, (txt, val)) in enumerate(info):
                text = '{}: {}'.format(txt, val)
                cv2.putText(frame, text, (10, (i * 20) + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_RED, 2)

            # Save the output video to file
            # if args.image:
            #     cv2.imwrite(os.path.join(args.output_dir, output_file), frame.astype(np.uint8))
            # else:
            #     video_writer.write(frame.astype(np.uint8))

            cv2.imshow(wind_name, frame)

            key = cv2.waitKey(1)
            if key == 27 or key == ord('q'):
                print('[i] ==> Interrupted by user!')
                break

        cap.release()
        cv2.destroyAllWindows()

        print('==> All done!')
        print('***********************************************************')


if __name__ == '__main__':
    _main()
