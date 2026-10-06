# Early-experience public schema audit v1

**SCHEMA ONLY — NO RESEARCH DATA ROWS / NUMERIC OUTCOMES REPORTED.**

- files: **4**

## All seasons personality data.xlsx

- bytes: 44838
- content type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- schema type: xlsx
- sheet `Full_Data`: rows=990 cols=23 header=['Bat_no', 'Individual', 'Season', 'Sex', 'Origin', 'Colony', 'Colony type', 'Trial name', 'FaExposure', 'AgeExposure', 'DaysTillExp', 'Trial', 'TotalDays_TillTrial', 'DaysOut_TillTrial', 'time2exit', 'time2explore', 'time2action', 'ActiveTime_Sec', 'Boldness', 'boxes_activity', 'boxes_all_enter', 'AllActivityNormed', 'ExpuNIQUE']

## Calculate_time_and_distance.py

- bytes: 7845
- content type: application/octet-stream
- schema type: code
- relevant identifiers: ['Bat_navigation', 'Cumulate_distance', 'Imp_gps', 'Max_distance', 'bats', 'check_colony', 'colony', 'distance', 'distance_column', 'distance_column.append', 'distance_delta', 'distance_sum', 'extract_gps', 'gps', 'imp_gps', 'max_distance', 'max_distance_column', 'max_distance_column.append', 'max_distances', 'max_distances.append', 'outside', 'ref_gps', 'target_gps', 'threshold_distance']
- relevant strings: ['/Users/xingchen/Documents/PhD_learning/Bat_navigation/All_database/Vesper/2020-2021/Adva2', 'Cumulate_distance', 'Max_distance', 'distance: ']

## Exploraion in squares.xlsx

- bytes: 13056
- content type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- schema type: xlsx
- sheet `Exploration`: rows=20 cols=23 header=['Bat no.', 'Name', 'Season', 'Sex', 'Origin', 'Colony', 'No of squares on the grid', 'Total nights out', 'avg. squares per night', 'total in km2 ', 'average in km2 esch square 0.85 per night', 'Enrichment', 'Max age', 'Boldness_B1', 'Explore_B1', 'Active_B1', None, None, None, None, None, None, None]

## Outdoor data.xlsx

- bytes: 52518
- content type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- schema type: xlsx
- sheet `exit_time_temp_new`: rows=736 cols=10 header=['Bat_ID', 'Sex', 'Environmental condition', 'Origin', 'Date', 'NumberDaysOut', 'Time Out (Minute)', 'Max distance (meters)', 'Age (days)', 'Explored area']

