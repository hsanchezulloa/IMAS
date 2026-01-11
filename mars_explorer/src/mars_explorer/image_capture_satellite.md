---

#### **Satellite Mission Protocol 1: Panoramic Image Capture of Crater Terrain**

**Mission ID:** satellite_0, satellite_4, satellite_2, satellite_3  
**Target Nodes:** N5, N58, N121, N150  
**Terrain Type:** Crater  
**Communication Window:** Varies per node (7h to 5h)  

---

**Step 1: Sensor Initialization**  
- **Action:** Power up multispectral imaging sensors and ensure camera systems are operational.  
- **Details:** Set sensor resolution to high definition for detailed terrain mapping. Enable panoramic stitching mode.  

**Step 2: Positioning Over Target Node**  
- **Action:** Manually or autonomously position satellite directly above the target node (e.g., N5, N58).  
- **Details:** Use GPS coordinates provided in assignments JSON to align with the crater terrain. Ensure stable positioning within the communication window.  

**Step 3: Capture Sequence**  
- **Action:** Initiate panoramic image capture sequence.  
- **Details:** Capture multiple overlapping images (minimum 10) to ensure complete coverage of the crater terrain. Adjust exposure settings based on lighting conditions (e.g., adjust shutter speed for low-light environments).  

**Step 4: Data Validation**  
- **Action:** Review captured images for completeness and quality.  
- **Details:** Ensure all images are free from artifacts and cover the entire target area. Stitch images together to form a panoramic mosaic.  

**Step 5: Data Transmission**  
- **Action:** Transmit validated data to ground control within the communication window.  
- **Details:** If communication loss occurs (e.g., at N150), store data locally for retransmission during the next available window.  

---

#### **Satellite Mission Protocol 2: Thermal Anomaly Detection on Icy Nodes**

**Mission ID:** satellite_1, satellite_5  
**Target Nodes:** N56, N112  
**Terrain Type:** Icy  
**Communication Window:** Varies per node (8h to 2h)  

---

**Step 1: Sensor Initialization**  
- **Action:** Power up thermal imaging sensors and ensure radiometric calibration is complete.  
- **Details:** Set sensor sensitivity to detect temperature variations in icy terrain. Enable anomaly detection algorithms.  

**Step 2: Positioning Over Target Node**  
- **Action:** Manually or autonomously position satellite directly above the target node (e.g., N56).  
- **Details:** Use GPS coordinates provided in assignments JSON to align with the icy terrain. Ensure stable positioning within the communication window.  

**Step 3: Capture Sequence**  
- **Action:** Initiate thermal anomaly detection sequence.  
- **Details:** Capture high-resolution thermal images at regular intervals (minimum every 5 minutes). Adjust sensor settings for optimal detection in icy conditions (e.g., compensate for ambient temperature).  

**Step 4: Data Validation**  
- **Action:** Analyze captured data for thermal anomalies and validate against baseline readings.  
- **Details:** Use onboard processing to identify anomalies and flag significant deviations from expected patterns.  

**Step 5: Data Transmission**  
- **Action:** Transmit validated data to ground control within the communication window.  
- **Details:** If communication loss occurs (e.g., at N112), store data locally for retransmission during the next available window.  

---

### Notes:  
- Ensure all missions are executed within their respective communication windows to avoid data loss.  
- For nodes with communication loss (e.g., N150, N78), implement local storage and priority-based transmission protocols.  
- Terrain type-specific adjustments (e.g., shutter speed for crater vs. icy terrain) must be applied during sensor initialization.  

--- 

This completes the transformation of raw satellite tasking data into precise, 5-step execution protocols for different imaging modalities.