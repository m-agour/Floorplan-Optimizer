import cv2
import os

image_folder = 'imgs'
video_name = 'Algorithm.mp4'

images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
delay = 0.3
fps = 1 / delay
video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

for image in images:
    img = cv2.imread(os.path.join(image_folder, image))
    for _ in range(int(fps * delay)):
        video.write(img)

cv2.destroyAllWindows()
video.release()
