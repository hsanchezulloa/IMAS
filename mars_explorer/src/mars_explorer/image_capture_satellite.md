### Technical Manual: Satellite Imaging Operations Protocol

---

#### **Mission 1: Capture Panoramic Images of Crater Terrain**

**Objective:** Acquire high-resolution panoramic images of crater terrain at nodes N5, N58, N121, and N150.

**Steps:**

1. **Sensor Initialization:**
   - Power up the multispectral imaging sensor.
   - Ensure camera calibration is complete (focus, exposure, white balance).
   - Verify communication link with ground station for real-time monitoring.

2. **Positioning:**
   - Orbit adjustment to achieve an altitude of 50 km above the target node.
   - Use star tracker and GPS for precise positioning over the designated crater locations.
   - Ensure nadir (directly downward) alignment for accurate terrain mapping.

3. **Capture Sequence:**
   - Enable panoramic stitching mode to combine multiple images into a single mosaic.
   - Capture 10 sequential images at intervals of 5 seconds, ensuring full coverage of the crater.
   - Use a shutter speed of 1/1000 second and ISO setting of 800 for sharp details in varying lighting conditions.

4. **Data Validation:**
   - Check image overlap (minimum 30%) and ensure no gaps in the mosaic.
   - Verify that all images are georeferenced with latitude, longitude, and timestamp.
   - Confirm that the final stitched image covers at least 95% of the target area.

5. **Transmission:**
   - Compress raw image files to reduce data size (lossless compression).
   - Transmit data packets via X-band communication link to ground station within 30 minutes post-capture.
   - Archive raw and processed images on-board for redundancy.

**Time Window:** Capture during local noon (12:00–14:00) to minimize shadows and maximize solar illumination.

---

#### **Mission 2: Identification of Thermal Anomalies at Icy Nodes**

**Objective:** Detect thermal anomalies in icy terrain at nodes N56 and N112.

**Steps:**

1. **Sensor Initialization:**
   - Activate the thermal infrared sensor (8–14 µm band).
   - Calibrate the sensor using on-board blackbody emitters.
   - Ensure data is being transmitted to the ground station for real-time analysis.

2. **Positioning:**
   - Orbit adjustment to achieve an altitude of 30 km above the target node.
   - Use thermal imaging to identify temperature gradients in the icy terrain.
   - Maintain a stable platform to minimize jitter (maximum 0.1° roll, pitch, yaw).

3. **Capture Sequence:**
   - Acquire thermal data in raster scan mode, capturing 20x20 pixel grid over each node.
   - Use a frame rate of 1 Hz for continuous monitoring.
   - Apply gain settings of 40 dB to enhance sensitivity to temperature variations.

4. **Data Validation:**
   - Check signal-to-noise ratio (SNR) ≥ 15 dB for all data points.
   - Identify anomalies as regions with temperature deviations >2 K from baseline readings.
   - Ensure georeferencing accuracy within ±50 m.

5. **Transmission:**
   - Transmit raw thermal data packets via S-band link to ground station immediately after capture.
   - Archive processed anomaly maps on-board for future reference.
   - Provide real-time alerts to the science team if anomalies exceed predefined thresholds.

**Time Window:** Capture during local midnight (23:00–01:00) when thermal contrast is maximized due to diurnal temperature variations.

---

### Final Answer

The above protocols provide a comprehensive 5-step execution plan for each satellite mission identified in the JSON file. Each protocol includes sensor initialization, positioning, capture sequence, data validation, and transmission steps, tailored to the specific terrain type (crater or icy) and mission requirements. The instructions are designed to ensure optimal image acquisition and data integrity while accounting for operational constraints such as altitude, timing, and communication protocols.