import cv2

# Define the codec and create a video writer object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# Iterate over the images in the folder
for i in range(1, 51):
    # Read the image
    img = cv2.imread(f'image_{i}.jpg')
    # Write the image to the video writer
    out.write(img)

# Release the video writer object
out.release()