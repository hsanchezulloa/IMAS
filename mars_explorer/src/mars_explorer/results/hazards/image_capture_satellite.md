Satellite Imaging Execution Protocols

---

#### **Mission Type 1: Panoramic Image Capture of Crater Terrain**

**Objective:** Capture high-resolution panoramic images of crater terrain at nodes N5, N58, N121, and N150.

**Execution Protocol:**

1. **Sensor Initialization:**
   - Power on the satellite's multi-spectral imaging sensors.
   - Conduct a pre-flight calibration check to ensure sensor accuracy.
   - Verify communication link stability with ground control.

2. **Positioning:**
   - Manually or automatically position the satellite over the target node (N5, N58, N121, or N150).
   - Adjust altitude to 50 km for optimal crater terrain visualization.
   - Ensure stable positioning within ±0.5 km deviation.

3. **Capture Sequence:**
   - Set exposure time to 10 seconds for detailed crater features.
   - Initiate panoramic image capture in a 360-degree sweep.
   - Capture images at intervals of 1 second, ensuring full coverage.

4. **Data Validation:**
   - Review captured images for clarity and completeness.
   - Check for any motion blur or data gaps.
   - Compare against predefined quality metrics (e.g., resolution ≥1m/pixel).

5. **Transmission:**
   - Transmit raw image data to ground station within the 7-hour communication window for N5, 4-hour for N58, 3-hour for N121, and 5-hour for N150.
   - Compress data if necessary to fit transmission bandwidth.

---

#### **Mission Type 2: Thermal Anomaly Detection at Icy Nodes**

**Objective:** Identify thermal anomalies at icy terrain nodes N56 and N112.

**Execution Protocol:**

1. **Sensor Initialization:**
   - Activate the satellite's thermal infrared sensors.
   - Perform a spectral response check to ensure sensor functionality.
   - Confirm communication link stability with ground control.

2. **Positioning:**
   - Manually or automatically position the satellite over target nodes N56 and N112.
   - Adjust altitude to 30 km for optimal thermal anomaly detection.
   - Ensure stable positioning within ±1 km deviation.

3. **Capture Sequence:**
   - Set frame rate to 1 Hz for continuous thermal monitoring.
   - Capture high-resolution thermal images in a grid pattern (1 km x 1 km).
   - Use radiometric calibration to correct temperature measurements.

4. **Data Validation:**
   - Analyze thermal data for anomalies exceeding baseline thresholds (e.g., >-50°C).
   - Check for consistency across multiple frames.
   - Ensure data integrity by comparing with reference datasets.

5. **Transmission:**
   - Transmit processed thermal data to ground station within the 8-hour communication window for N56 and 2-hour for N112.
   - Prioritize transmission of anomaly detection alerts immediately upon discovery.

---

### Notes:
- **Communication Loss Nodes:** Be aware that nodes N7, N78, and N150 may experience communication loss. Implement redundancy checks to ensure data integrity.
- **Altitude Adjustments:** Ensure altitude adjustments do not interfere with other satellite operations or exceed operational limits.
- **Terrain-Specific Settings:** Apply terrain-specific sensor settings (e.g., longer exposure times for craters, optimized thermal sensitivity for icy nodes).

---

This protocol ensures precise execution of satellite imaging missions, accounting for mission type, terrain specifics, and communication constraints.