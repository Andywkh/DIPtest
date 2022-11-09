from AOA_Calculations.sixRubberAntenna3ppl import *

from dynamic_plt.AOA_plot import *

fig = plt.figure()

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name

cap = cv2.VideoCapture('./Datasets/video/test3.mp4')

##### To Output Video when running #####
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('OutputVideo3new.avi', fourcc, 30.0, (1440,1080))
    
# Check if camera opened successfully
if (cap.isOpened()== False):
    print("Error opening video stream or file")

# Initializing 
calculatedAOA_T1 = 0
calculatedAOA_T2 = 0
calculatedAOA_T3 = 0
frameNumber = 0

final_gtaoa = [[],[],[]]
final_calculatedaoa = [[],[],[]]

# Read until video is completed
while (cap.isOpened()):

# Capture frame-by-frame
    ret, frame = cap.read()
    print('frame shape: ', np.shape(frame))
    if not ret:
        break
    timestampe_for_frame = cv_data_T1.get_time_for_frame(frameNumber)
    # gtaoa_tan_for_frame_T1 = cv_data_T1.get_tan_for_frame(frameNumber)
    # gtaoa_tan_for_frame_T2 = cv_data_T2.get_tan_for_frame(frameNumber)
    gtaoa_cu_for_frame_T1 = cv_data_T1.get_cu_for_frame(frameNumber)
    gtaoa_cu_for_frame_T2 = cv_data_T2.get_cu_for_frame(frameNumber)
    gtaoa_cu_for_frame_T3 = cv_data_T3.get_cu_for_frame(frameNumber)
    
    print(frameNumber)
    frameNumber += 1

    # Declaring Time & Phase 
    phaseList_T1 = time_function(time_value = timestampe_for_frame, RFID_data = RFID_data_T1)
    phaseList_T2 = time_function(time_value = timestampe_for_frame, RFID_data = RFID_data_T2)
    phaseList_T3 = time_function(time_value = timestampe_for_frame, RFID_data = RFID_data_T3)
    

    # Finding & Calculating AOA
    calculatedAOA_T1_new, valid_T1 = Aoa_calculation_function(phaseList = phaseList_T1)
    calculatedAOA_T2_new, valid_T2 = Aoa_calculation_function(phaseList = phaseList_T2)
    calculatedAOA_T3_new, valid_T3 = Aoa_calculation_function(phaseList = phaseList_T3)
    
    if valid_T1:
        calculatedAOA_T1 = calculatedAOA_T1_new
    if valid_T2:
        calculatedAOA_T2 = calculatedAOA_T2_new
    if valid_T3:
        calculatedAOA_T3 = calculatedAOA_T3_new
        
    #1080p
    # fx = 528.6107177
    # u_0 = 630.80725

    fx = 1060
    u_0 = 970
    # u_gt_T1 = fx * math.tan(gtaoa_tan_for_frame_T1) + u_0
    # u_gt_T2 = fx * math.tan(gtaoa_tan_for_frame_T2) + u_0   
    u_gt_T1 =  gtaoa_cu_for_frame_T1
    u_gt_T2 =  gtaoa_cu_for_frame_T2
    u_gt_T3 =  gtaoa_cu_for_frame_T3
    ###### Draw the gt AOA (cv) ######
    # RFID Tag 1 (John)
    start_point = (int(u_gt_T1), 0)
    end_point = (int(u_gt_T1), 1080)
    color = (255, 0, 0)
    thickness = 3
    frame = cv2.line(frame, start_point, end_point, color, thickness)
    
    # RFID Tag 2 (SiMin)
    start_point = (int(u_gt_T2), 0)
    end_point = (int(u_gt_T2), 1080)
    color = (0, 255, 0)
    thickness = 3
    frame = cv2.line(frame, start_point, end_point, color, thickness)

    # RFID Tag 4 (Deva)
    start_point = (int(u_gt_T3), 0)
    end_point = (int(u_gt_T3), 1080)
    color = (0, 0, 255)
    thickness = 3
    frame = cv2.line(frame, start_point, end_point, color, thickness)
    
    ###### Draw the calculated/estimated AOA (cv) ######
    # RFID_Tag 1 (John)    
    u_T1 = fx * math.tan(calculatedAOA_T1) + u_0
    start_point_T1 = (int(u_T1), 0)
    end_point_T1 = (int(u_T1), 1080)
    color = (255, 255, 0)
    thickness = 3
    frame = cv2.line(frame, start_point_T1, end_point_T1, color, thickness)

    # RFID_Tag 2 (SiMin)   
    u_T2 = fx * math.tan(calculatedAOA_T2) + u_0
    start_point_T2 = (int(u_T2), 0)
    end_point_T2 = (int(u_T2), 1080)
    color = (0, 255, 255)
    thickness = 3
    frame = cv2.line(frame, start_point_T2, end_point_T2, color, thickness)

    #RFID_Tag 4 (Deva)   
    u_T3 = fx * math.tan(calculatedAOA_T3) + u_0
    start_point_T3 = (int(u_T3), 0)
    end_point_T3 = (int(u_T3), 1080)
    color = (255, 255, 255)
    thickness = 3
    frame = cv2.line(frame, start_point_T3, end_point_T3, color, thickness)

    print(calculatedAOA_T1, calculatedAOA_T2, calculatedAOA_T3)

    ##save the result each frame
    if frameNumber > 1500 and frameNumber < 2100: # do not use the first 5 sec' data
        final_gtaoa[0].append(u_gt_T1)
        final_gtaoa[1].append(u_gt_T2)
        final_gtaoa[2].append(u_gt_T3)
        final_calculatedaoa[0].append(u_T1)
        final_calculatedaoa[1].append(u_T2)
        final_calculatedaoa[2].append(u_T3)
    if  frameNumber  > 2100:
        break

    #Video Resolution Change
    # Display the resulting frame
    resize = cv2.resize(frame,(1440,1080))
    cv2.imshow('Frame', resize)
    out.write(resize)
    
    #Graph Plotting

    #graph_plotting_per_unit_timefunction(calculatedAOA = calculatedAOA_T1, timestampe_for_frame)
    #graph_plotting_per_unit_timefunction(calculatedAOA = calculatedAOA_T2, timestampe_for_frame)
    #graph_plotting_per_unit_timefunction(calculatedAOA = calculatedAOA_T3, timestampe_for_frame)

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
## calculate mean error betweem each pairs of CV-RFID
mean_absolute_error = np.zeros((3,3))
for i in range(3):
    for j in range(3):
        mean_absolute_error[i,j] = np.mean(np.abs(np.array(final_gtaoa[i]) - np.array(final_calculatedaoa[j])))
print(mean_absolute_error)
# visualize the error with a heat map
fig, ax = plt.subplots()
plt.xticks(ticks = np.arange(3))
plt.yticks(ticks = np.arange(3))
plt.xlabel('CV obj.')
plt.ylabel('RFID tag')
hm = ax.imshow(mean_absolute_error, cmap='Blues', interpolation = 'nearest')
plt.colorbar(hm)

plt.savefig('OutputPics/------.png')
plt.show()

fig, ax = plt.subplots()
plt.xlabel('Frame Number < 30 frames = 1s >')
plt.ylabel('Pixel Location in x-axis')
ax.plot(final_gtaoa[0], label = 'gtaoa_#1')
ax.plot(final_gtaoa[1], label = 'gtaoa_#2')
ax.plot(final_gtaoa[2], label = 'gtaoa_#3')
ax.plot(final_calculatedaoa[0], label = 'cal.aoa_#1')
ax.plot(final_calculatedaoa[1], label = 'cal.aoa_#2')
ax.plot(final_calculatedaoa[2], label = 'cal.aoa_#3')
plt.legend()
plt.savefig('OutputPics/++++++++++.png')
plt.show()


# When everything done, release the video capture object
cap.release()
out.release()
# Closes all the frames
cv2.destroyAllWindows()