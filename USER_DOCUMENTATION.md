# End-User Manual & Interface Guide

This guide walks you through navigating the application interface, reading data panels, and troubleshooting performance expectations.

## Step-by-Step Usage

### 1. Launching the App
Run your local `weather.py` file. A dashboard measuring `480x690` will open centered on your desktop screen with the keyboard focus automatically snapped inside the central input tray.

### 2. Searching for a City
* Enter any worldwide municipal name (e.g., *London*, *Tokyo*, *Rourkela*) into the input field.
* Click **Search**. 
* The system fetches matching coordinates instantly, populating your main pane with the current temperature and structural weather classifications.

### 3. Reviewing Extended Metrical Blocks
* Click the blue **More Details →** button below the core temperature readout.
* A contextual secondary window will populate, breaking down exact humidity levels, localized wind configurations, and morning/evening boundary markers across a three-day window.

### 4. Viewing Local Query Archives
* Click directly on the descriptive weather condition text label (e.g., *"Clear Sky\nClick to View History"*).
* This action launches the **Historical Search Records Grid**, rendering a tabular timestamped log of your machine's unique lookup patterns.

## Interface Component Breakdown

| Visual Element | User Action Trigger | Interface Event Response |
| :--- | :--- | :--- |
| **Search Input** | Typing text + clicking 'Search' | Queries Geocoding service; shifts main weather states. |
| **More Details Button** | Single Click | Toggles 3-Day detailed parameters modal container. |
| **Condition Label** | Single Click | Pops up a tabular database layout window. |
| **Dismiss Log Button** | Single Click | Safely unbinds and terminates top-level child popups. |