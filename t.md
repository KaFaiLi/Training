# Data Visualization Task: Custom Time Series Plot for Financial Products

## Context
I need to create a comprehensive visualization of financial product data across time. The existing `custom_plot_visualization.py` needs to be completely rewritten with a new visualization approach.

## Dataset Description
The dataset contains the following columns:
- **Product**: Categories including 'bond', 'future', and 'irdswap'
- **Projected Pillar**: Time horizons such as '100Y', '10Y', '15Y', '1M', '1W', '1Y', '20Y', '25Y', '2Y', '30Y', '3M', '40Y', '50Y'
- **pricingdate**: Dates ranging from 2023 to 2025 in format 'M/D/YYYY' (e.g., '2/28/2023')
- **Validated Value Projected CV**: Float numbers representing values
- **Outlier**: Binary indicator (0/1), with null values possible for 'irdswap'
- **Is Auction Date**: Binary indicator (0/1)

## Visualization Requirements

### Plot 1: Aggregated Time Series
- Create a time series plot showing 'Validated Value Projected CV' over time (x-axis: pricingdate)
- Display separate lines for different products ('bond', 'future')
- Highlight data points where Outlier = 1 with a distinctive marker and color
- Add vertical lines on dates where 'Is Auction Date' = 1
- Include a legend that clearly distinguishes products, outliers, and auction dates
- This plot should aggregate data from all Projected Pillars

### Plot 2: Pillar-Specific Time Series
- Create a function to generate time series plots filtered by a specific Projected Pillar
- For example, show bond and future projected CV values specifically for Projected Pillar = '100Y'
- Highlight outliers and auction dates specific to the selected Projected Pillar
- Include interactive elements if possible (e.g., dropdown to select different Projected Pillars)
- Ensure proper labeling and visual clarity for each pillar-specific plot

## Technical Requirements
- Use matplotlib, seaborn, or plotly for visualization
- Ensure code is modular and well-documented
- Handle potential missing values appropriately
- Optimize for readability and performance
- Include appropriate titles, legends, and axis labels
- Use a visually appealing color scheme with good contrast for accessibility
- Create functions that can be easily reused and modified

## Expected Output
- A complete Python script that replaces the current `custom_plot_visualization.py`
- Functions for both aggregated and pillar-specific visualizations
- Clean, well-documented code with appropriate comments