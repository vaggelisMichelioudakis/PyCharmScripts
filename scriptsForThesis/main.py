from geomeppy import IDF

# 1. Point Geomeppy to your EnergyPlus "Dictionary" file.
idd_file = "/Users/vaggelismixelioudakis/Desktop/Energy+/Energy+.idd"
IDF.setiddname(idd_file)

# 2. Load your updated baseline file
input_idf = "/Users/vaggelismixelioudakis/Desktop/Building/ASHRAE901_OfficeMedium_STD2019-WWR0.6/ASHRAE901_OfficeMedium_STD2019_Atlanta_25.2.idf"
idf = IDF(input_idf)

# 3. With this command we change the WWR value for our windows
# Since in our selected building the windows are simple and all the same we used the "construction" variable
idf.set_wwr(0.9, construction="Window_U_0.424_SHGC_South_0.249", force=True)

# 4. Save the new file to your Desktop
output_idf = "/Users/vaggelismixelioudakis/Desktop/Atlanta_WWR_090_Finland.idf"
idf.saveas(output_idf)

print(f"Success! Saved new file to {output_idf}")