---

# Satellite Imaging Operations Manual  

## 1. Panoramic Image Capture of Crater Terrain  

**Mission Type:** Capture panoramic images of **crater** terrain at nodes **N5**, **N58**, **N121**, and **N150**.  

### Step-by-Step Protocol:  

#### 1. Sensor Initialization  
- **Action:** Power up the multi-spectral imager (MSI) and stereo camera system.  
- **Details:** Ensure the MSI is set to wide-angle mode for panoramic coverage. Calibrate sensors to account for varying lighting conditions.  
- **Time Window:** Acquire images during optimal sun angles (e.g., 10:00–14:00 local time) for maximum surface detail.  

#### 2. Positioning  
- **Action:** Adjust satellite altitude to **300 km** for high-resolution imaging.  
- **Details:** Ensure the satellite is in a stable orbit over the target nodes. Orient cameras nadir-pointing (directly downward).  
- **Validation:** Confirm positioning via GPS and attitude control systems.  

#### 3. Capture Sequence  
- **Action:** Begin image capture sequence at each node.  
- **Details:** Take sequential images with overlapping coverage to stitch into a panoramic mosaic. Use stereo imaging for 3D terrain mapping.  
- **Parameters:** Set shutter speed to **1/1000 second** and ISO to **800** for sharp, high-resolution images.  

#### 4. Data Validation  
- **Action:** Review captured images for clarity and completeness.  
- **Details:** Check for artifacts, blur, or missing coverage areas. Use onboard software to stitch images into a panoramic mosaic.  
- **Validation Criteria:** Ensure all nodes are fully covered with no gaps in the mosaic.  

#### 5. Transmission  
- **Action:** Compress and encrypt the image data. Transmit via satellite downlink to ground station at **Nairobi, Kenya**.  
- **Details:** Use secure encryption protocols (e.g., AES-256) for data transmission. Schedule follow-up passes if additional coverage is needed.  

---

## 2. Thermal Anomaly Identification at Icy Nodes  

**Mission Type:** Identify thermal anomalies at **icy** nodes **N56** and **N112**.  

### Step-by-Step Protocol:  

#### 1. Sensor Initialization  
- **Action:** Power up the thermal infrared imager (TIR) and multispectral scanner (MSS).  
- **Details:** Set TIR to high-sensitivity mode for detecting temperature variations. Calibrate MSS to capture visible and near-infrared bands.  
- **Time Window:** Acquire images during local night hours (e.g., 18:00–24:00) for thermal contrast.  

#### 2. Positioning  
- **Action:** Adjust satellite altitude to **250 km** for enhanced thermal resolution.  
- **Details:** Ensure the satellite is in a stable orbit over the target nodes. Orient cameras nadir-pointing (directly downward).  
- **Validation:** Confirm positioning via GPS and attitude control systems.  

#### 3. Capture Sequence  
- **Action:** Begin thermal anomaly detection at each node.  
- **Details:** Take high-resolution images in both TIR and visible spectrum for cross-referencing. Use automated algorithms to detect temperature anomalies.  
- **Parameters:** Set exposure time to **2 seconds** for TIR imaging and ISO to **400** for visible light.  

#### 4. Data Validation  
- **Action:** Analyze thermal images for anomalies (e.g., hotspots or irregular patterns).  
- **Details:** Cross-reference with visible spectrum images to confirm findings. Use onboard software to flag potential anomalies for ground analysis.  
- **Validation Criteria:** Ensure all flagged anomalies are within acceptable thermal variation thresholds.  

#### 5. Transmission  
- **Action:** Compress and encrypt the image data. Transmit via satellite downlink to ground station at **Huntsville, Alabama**.  
- **Details:** Use secure encryption protocols (e.g., AES-256) for data transmission. Schedule follow-up passes if additional thermal anomalies are detected.  

---

### Notes:  
- Ensure all imaging operations adhere to power and data storage constraints.  
- Monitor satellite health and safety throughout the mission.  
- Follow standard operating procedures for sensor calibration and data integrity.  

--- 

This manual provides a comprehensive guide for executing satellite imaging missions as specified in the JSON file. Each protocol is designed to ensure optimal results based on terrain type, priority level, and operational constraints.