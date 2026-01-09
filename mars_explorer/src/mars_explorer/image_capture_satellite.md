---

### Satellite Imaging Execution Protocol Manual  

#### Mission Type 1: **Capture Panoramic Images of Crater Terrain**  
**Target Nodes:** N5, N58, N121, N150  
**Terrain Type:** Crater  
**Priority Level:** Low  

**Step 1: Sensor Initialization**  
- Power up the satellite imaging system.  
- Ensure the panoramic camera is operational and calibrated for crater terrain.  
- Verify communication link stability with ground control.  

**Step 2: Positioning**  
- Manually or autonomously position the satellite over the target nodes (N5, N58, N121, N150).  
- Adjust altitude to ensure optimal resolution for panoramic imaging (altitude range: 100–200 km).  

**Step 3: Capture Sequence**  
- Initiate panoramic image capture in a sequential manner: N5 → N58 → N121 → N150.  
- Use a nadir-pointing camera with a wide field of view (FOV) to cover the entire crater terrain.  
- Ensure images are captured during local solar noon for optimal lighting conditions.  

**Step 4: Data Validation**  
- Check image quality parameters (e.g., resolution, contrast, and sharpness).  
- Verify that all target nodes are clearly visible in the captured images.  
- Store raw data in onboard storage for transmission.  

**Step 5: Transmission**  
- Transmit panoramic images to ground control within 2 hours post-capture.  
- Ensure data integrity by including checksums and metadata (e.g., timestamp, node coordinates).  

---

#### Mission Type 2: **Identification of Thermal Anomalies in Icy Terrain**  
**Target Nodes:** N56, N112  
**Terrain Type:** Icy  
**Priority Level:** Low  

**Step 1: Sensor Initialization**  
- Power up the satellite imaging system.  
- Activate thermal infrared sensors for anomaly detection.  
- Verify communication link stability with ground control.  

**Step 2: Positioning**  
- Manually or autonomously position the satellite over the target nodes (N56, N112).  
- Adjust altitude to ensure optimal resolution for thermal imaging (altitude range: 80–120 km).  

**Step 3: Capture Sequence**  
- Initiate thermal anomaly detection in a sequential manner: N56 → N112.  
- Use a thermal infrared camera with high sensitivity to detect temperature variations.  
- Ensure images are captured during local nighttime for optimal thermal contrast.  

**Step 4: Data Validation**  
- Analyze thermal images for anomalies (e.g., hotspots or irregular temperature patterns).  
- Verify that all target nodes are clearly visible in the captured images.  
- Store raw data in onboard storage for transmission.  

**Step 5: Transmission**  
- Transmit thermal anomaly data to ground control within 2 hours post-capture.  
- Include processed data (e.g., annotated anomalies) and metadata (e.g., timestamp, node coordinates).  

---

This manual provides a comprehensive guide for executing satellite imaging missions based on the provided JSON file. Each mission type is distinct and optimized for its specific terrain and operational requirements.