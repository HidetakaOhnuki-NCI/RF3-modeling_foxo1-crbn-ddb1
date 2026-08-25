# Panel A visualization

`panel_a_interface.cxc` reproduces the visual style used for the representative
GSPT1-CC-90009-CRBN interface. It was prepared for UCSF ChimeraX 1.12.

Before running it:

1. Copy the command file to a working location.
2. Replace `MODEL_PATH` with the path to the representative PDB model.
3. Replace `OUTPUT_PATH` with the desired PNG path.
4. Open the command file in ChimeraX or run ChimeraX with the command file as
   its input.

The script assumes model 1 and chains A=DDB1, B=CRBN, F=GSPT1, L=CC-90009,
and M=Zn. DDB1 is not displayed in the close-up. GSPT1 and CRBN are yellow and
blue, respectively. CC-90009 is shown as sticks. Gray dashed pseudobonds mark
GSPT1-CRBN heavy-atom pairs separated by 3.6 A or less.

The representative structure file is not included in this GitHub package. Its
checksum and external repository identifier should be recorded in the raw-model
manifest when the structure is deposited.
