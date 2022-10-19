from AOA_Calculations.sixRubberAntenna import *

from dynamic_plt.AOA_plot import *
fig = plt.figure()

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
    
#cap = cv2.VideoCapture('../Datasets/video/testing4.mp4')

cap = cv2.VideoCapture('./Datasets/video/testing4.mp4')
    
# Check if camera opened successfully
if (cap.isOpened()== False):
    print("Error opening video stream or file")
    
frameNumber = 0
# Read until video is completed
while (cap.isOpened()):
# Capture frame-by-frame
    ret, frame = cap.read()
    timestampe_for_frame = cv_data.get_time_for_frame(frameNumber)
    gtaoa_tan_for_frame = cv_data.ctan[0][frameNumber]
    # print('sdgfhjsdgfsd',cv_data.ctan)
    frameNumber += 1
    #for x in range(len(timeList)):
            
        #print(timestampe_for_frame)

            #declaring time
    phaseList = time_function(time_value = timestampe_for_frame, RFID_data = RFID_data)
        
        #print(phaseList)

    #f1inding AOA
    calculatedAOA = Aoa_calculation_function(phaseList)

        #1080p
        # fx = 528.6107177
        # u_0 = 630.80725

    fx = 1060
    u_0 = 970
    u_gt = fx * math.tan(gtaoa_tan_for_frame) + u_0
        
        # draw the gt aoa (cv)
    start_point = (int(u_gt), 0)
    end_point = (int(u_gt), 1080)
    color = (0, 0, 255)
    thickness = 3
    frame = cv2.line(frame, start_point, end_point, color, thickness)
        # draw the estimated aoa (rfid)
        # for i in range(5):
        #     u = fx * math.tan(calculatedAOA[i]) + u_0
        #     start_point = (int(u), 0)
        #     end_point = (int(u), 1080)
        #     color = (0, 255, 255)
        #     thickness = 3
        #     frame = cv2.line(frame, start_point, end_point, color, thickness)
    u = fx * math.tan(calculatedAOA) + u_0
    start_point = (int(u), 0)
    end_point = (int(u), 1080)
    color = (0, 255, 255)
    thickness = 3
    frame = cv2.line(frame, start_point, end_point, color, thickness)
        #Video Resolution Change
        # Display the resulting frame
    resize = cv2.resize(frame,(1440,1080))
    cv2.imshow('Frame', resize)

    #Graph Plotting
    graph_plotting_per_unit_timefunction(calculatedAOA, timestampe_for_frame)

        # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    
# When everything done, release the video capture object
cap.release()
    
# Closes all the frames
cv2.destroyAllWindows()