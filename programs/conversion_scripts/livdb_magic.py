#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
from past.utils import old_div
import wx
import sys
import math
import os
import scipy
from scipy import *
# import pmagpy_tests  # pmagpy can be imported IF dialogs or pmagpy_tests is imported first
import programs
from pmagpy import pmag
from pmagpy import ipmag
from pmagpy import new_builder as nb
from dialogs import pmag_widgets as pw


# ------


# ===========================================
# GUI
# ===========================================


class convert_livdb_files_to_MagIC(wx.Frame):
    """"""
    title = "Convert Livdb files to MagIC format"

    def __init__(self, WD):
        wx.Frame.__init__(self, None, wx.ID_ANY, self.title)
        self.panel = wx.Panel(self)
        self.max_files = 10
        self.WD = WD
        self.create_menu()
        self.InitUI()
        self.data_model_num = int(pmag.get_named_arg_from_sys("-DM", 3))

        if "-WD" in sys.argv:
            ind = sys.argv.index('-WD')
            self.WD = sys.argv[ind+1]
        else:
            self.WD = "."
        self.WD = os.path.realpath(self.WD)
        os.chdir(self.WD)


    def create_menu(self):
        """ Create menu
        """
        self.menubar = wx.MenuBar()

        menu_about = wx.Menu()
        menu_help = menu_about.Append(-1, "&Some notes", "")
        self.Bind(wx.EVT_MENU, self.on_menu_help, menu_help)

        self.menubar.Append(menu_about, "& Instructions")

        self.SetMenuBar(self.menubar)

    def on_menu_help(self, event):

        dia = message_box("Instructions")
        dia.Show()
        dia.Center()

    def InitUI(self):

        pnl = self.panel

        # ---sizer infor ----

        TEXT1 = "Instructions:\n"
        TEXT2 = "Put all livdb files of the same Location in one folder\n"
        TEXT3 = "If there is a more than one location, use multiple folders\n"
        TEXT4 = "Each measurement file must end with '.livdb' or .livdb.csv\n"

        TEXT = TEXT1+TEXT2+TEXT3+TEXT4
        bSizer_info = wx.StaticBoxSizer(wx.StaticBox(
            self.panel, wx.ID_ANY, ""), wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        # ---sizer 1 ----
        TEXT = "File:\n Choose a working directory path\n No spaces are allowed in path"
        bSizer1 = wx.StaticBoxSizer(wx.StaticBox(
            self.panel, wx.ID_ANY, ""), wx.VERTICAL)
        bSizer1.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_TOP)
        bSizer1.AddSpacer(5)
        self.dir_paths = {}
        self.add_dir_btns = {}
        self.bSizers_1 = {}
        self.bSizers_2 = {}
        for i in range(self.max_files):
            self.dir_paths[i] = wx.TextCtrl(self.panel, id=-1, size=(200,25), style=wx.TE_READONLY)
            self.add_dir_btns[i] = wx.Button(self.panel, id=-1, label='add',name='add_{}'.format(i))
            self.Bind(wx.EVT_BUTTON, self.on_add_dir_button_i, self.add_dir_btns[i])
            self.bSizers_1[i] = wx.BoxSizer(wx.HORIZONTAL)
            self.bSizers_1[i].Add(wx.StaticText(pnl,label=('{}  '.format(i)[:2])),wx.ALIGN_LEFT)
            self.bSizers_1[i].Add(self.dir_paths[i], wx.ALIGN_LEFT)
            self.bSizers_1[i].Add(self.add_dir_btns[i], wx.ALIGN_LEFT)
            bSizer1.Add(self.bSizers_1[i], wx.ALIGN_TOP)
            bSizer1.AddSpacer(5)

        # ---sizer 2 ----

        TEXT = "\nLocation:\n"
        bSizer2 = wx.StaticBoxSizer(wx.StaticBox(
            self.panel, wx.ID_ANY, ""), wx.VERTICAL)
        bSizer2.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_TOP)
        bSizer2.AddSpacer(5)
        self.file_locations = {}
        for i in range(self.max_files):
            self.file_locations[i] = wx.TextCtrl(self.panel, id=-1, size=(60,25))
            bSizer2.Add(self.file_locations[i], wx.ALIGN_TOP)
            bSizer2.AddSpacer(5)

# ---sizer 3 ----
##
# missing

        # ---sizer 4 ----

        TEXT = "\nSample-specimen\nnaming convention:"
        bSizer4 = wx.StaticBoxSizer(wx.StaticBox(
            self.panel, wx.ID_ANY, ""), wx.VERTICAL)
        bSizer4.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_TOP)
        self.sample_naming_conventions = [
            'sample=specimen', 'no. of terminate characters', 'character delimited']
        bSizer4.AddSpacer(5)
        self.naming_con_boxes = {}
        self.naming_con_char = {}
        for i in range(self.max_files):
            self.naming_con_boxes[i] = wx.ComboBox(self.panel, -1, self.sample_naming_conventions[0], size=(180,25), choices=self.sample_naming_conventions, style=wx.CB_DROPDOWN)
            self.naming_con_char[i] = wx.TextCtrl(self.panel, id=-1, size=(40,25))
            bSizer = wx.BoxSizer(wx.HORIZONTAL)
            bSizer.Add(self.naming_con_boxes[i], wx.ALIGN_LEFT)
            bSizer.Add(self.naming_con_char[i], wx.ALIGN_LEFT)
            bSizer4.Add(bSizer, wx.ALIGN_TOP)
            bSizer4.AddSpacer(5)

        # ---sizer 5 ----

        TEXT = "\nSite-sample\nnaming convention:"
        bSizer5 = wx.StaticBoxSizer(wx.StaticBox(
            self.panel, wx.ID_ANY, ""), wx.VERTICAL)
        bSizer5.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_TOP)
        self.site_naming_conventions = [
            'site=sample', 'no. of terminate characters', 'character delimited']
        bSizer5.AddSpacer(5)
        self.site_name_conventions = {}
        self.site_name_chars = {}
        for i in range(self.max_files):
            self.site_name_chars[i] = wx.TextCtrl(self.panel, id=-1, size=(40,25))
            self.site_name_conventions[i] = wx.ComboBox(self.panel, -1, self.site_naming_conventions[0], size=(180,25), choices=self.site_naming_conventions, style=wx.CB_DROPDOWN)
            bSizer = wx.BoxSizer(wx.HORIZONTAL)
            bSizer.Add(self.site_name_conventions[i], wx.ALIGN_LEFT)
            bSizer.Add(self.site_name_chars[i], wx.ALIGN_LEFT)
            bSizer5.Add(bSizer, wx.ALIGN_TOP)
            bSizer5.AddSpacer(5)

        # ------------------

        self.okButton = wx.Button(self.panel, wx.ID_OK, "&OK")
        self.Bind(wx.EVT_BUTTON, self.on_okButton, self.okButton)

        self.cancelButton = wx.Button(self.panel, wx.ID_CANCEL, '&Cancel')
        self.Bind(wx.EVT_BUTTON, self.on_cancelButton, self.cancelButton)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        # hbox1.Add(self.add_file_button)
        #hbox1.Add(self.remove_file_button )

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.okButton)
        hbox2.Add(self.cancelButton)

        # ------

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddSpacer(5)
        hbox.Add(bSizer1, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(5)
        hbox.Add(bSizer2, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(5)
##        hbox.Add(bSizer3, flag=wx.ALIGN_LEFT)
# hbox.AddSpacer(5)
        hbox.Add(bSizer4, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(5)
        hbox.Add(bSizer5, flag=wx.ALIGN_LEFT)
        hbox.AddSpacer(5)

        # -----

        vbox.AddSpacer(20)
        vbox.Add(bSizer_info, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vbox.AddSpacer(20)
        vbox.Add(hbox)
        vbox.AddSpacer(20)
        vbox.Add(hbox1, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vbox.AddSpacer(20)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vbox.AddSpacer(20)

        self.panel.SetSizer(vbox)
        vbox.Fit(self)
        self.Show()
        self.Centre()

    def on_add_dir_button_i(self, event):

        dlg = wx.DirDialog(
            None, message="choose directory with livdb files",
            defaultPath=self.WD,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            FILE = dlg.GetPath()
        # fin=open(FILE,'r')
        button = event.GetEventObject()
        name = button.GetName()
        i = int((name).split("_")[-1])
        # print "The button's name is " + button.GetName()

        self.dir_paths[i].SetValue(FILE)

    def read_generic_file(self, path):
        Data = {}
        Fin = open(path, 'r')
        header = Fin.readline().strip('\n').split('\t')

        for line in Fin.readlines():
            tmp_data = {}
            l = line.strip('\n').split('\t')
            if len(l) < len(header):
                continue
            else:
                for i in range(len(header)):
                    tmp_data[header[i]] = l[i]
                specimen = tmp_data['Specimen']
                if specimen not in list(Data.keys()):
                    Data[specimen] = []
                # check dupliactes
                if len(Data[specimen]) > 0:
                    if tmp_data['Treatment (aka field)'] == Data[specimen][-1]['Treatment (aka field)']:
                        print("-W- WARNING: duplicate measurements specimen %s, Treatment %s. keeping onlt the last one" %
                              (tmp_data['Specimen'], tmp_data['Treatment (aka field)']))
                        Data[specimen].pop()

                Data[specimen].append(tmp_data)
        return(Data)

    def on_okButton(self, event):

        meas_files = []
        spec_files = []

        for i in range(self.max_files):

            # read directory path
            dirpath = self.dir_paths[i].GetValue()
            if dirpath != "":
                dir_name = str(dirpath.split("/")[-1])
            else:
                continue

            # get location
            location_name = self.file_locations[i].GetValue()
            # get sample-specimen naming convention
            samp_con = str(self.naming_con_boxes[i].GetValue())
            samp_chars = str(self.naming_con_char[i].GetValue())
            samp_chars = samp_chars.strip('"').strip("'")
            if samp_con == "character delimited" and not samp_chars:
                pw.simple_warning("To delimit samples by character, you must provide the delimiter, (eg. \"-\" or \"_\")!")
                return
            # get site-sample naming convention
            site_con = str(self.site_name_conventions[i].GetValue())
            site_chars = str(self.site_name_chars[i].GetValue())
            site_chars = site_chars.strip('"').strip("'")
            if site_con == "character delimited" and not site_chars:
                pw.simple_warning("To delimit sites by character, you must provide the delimiter, (eg. \"-\" or \"_\")!")
                return

            # name output files
            if self.data_model_num == 2:
                meas_out = "magic_measurements_{}.txt".format(i)
                spec_out = "er_specimens_{}.txt".format(i)
            else:
                meas_out = "measurements_{}.txt".format(i)
                spec_out = "specimens_{}.txt".format(i)
            # do conversion
            convert(dir_name, meas_out, spec_out,
                    samp_con, samp_chars, site_con,
                    site_chars, location_name)
            meas_files.append(meas_out)
            spec_files.append(spec_out)

        if self.data_model_num == 2:
            res = ipmag.combine_magic(meas_files, "magic_measurements.txt", 2)
            ipmag.combine_magic(spec_files, "er_specimens.txt", 2)
        else:
            res = ipmag.combine_magic(meas_files, "measurements.txt", 2)
            ipmag.combine_magic(spec_files, "specimens.txt", 2)
            con = nb.Contribution(".", read_tables=['measurements', 'specimens'])
            con.propagate_measurement_info()
            for dtype in ['samples', 'sites', 'locations']:
                if dtype in con.tables:
                    con.write_table_to_file(dtype)

        pmag.remove_files(meas_files)
        pmag.remove_files(spec_files)
        if res:
            self.after_convert_dia()
        else:
            pw.simple_warning("Something when wrong with one or more of your files.\nSee Terminal/Command Prompt output for more details")


    def after_convert_dia(self):
        dlg1 = wx.MessageDialog(
            None, caption="Message:", message="file converted!\n you can try running thellier gui...\n", style=wx.OK | wx.ICON_INFORMATION)
        dlg1.ShowModal()
        dlg1.Destroy()
        self.Destroy()


    def on_cancelButton(self, event):
        self.Destroy()




class message_box(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, title):
        wx.Frame.__init__(self, parent=None, size=(1000, 500))

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_log = wx.TextCtrl(
            self.panel, id=-1, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.sizer.Add(self.text_log, 1, wx.EXPAND)
        TEXT = '''
            #--------------------------------------
            #
            # Livdb Database structure
            #
            # HEADER:
            # 1) First line is the header.
            #    The header includes 19 fields delimited by comma (',')
            #    Notice: space is not a delimiter !
            #    In the list below the delimiter is not used, and the concersion script assumes comma delimited file
            #
            # Header fields:
            # Sample code (string): (delimiter = space+)
            # Sample Dip (degrees): (delimiter = space)
            # Sample Dec (degrees): (delimiter = space)
            # Height (meters): (delimiter = space)
            # Position (no units): (delimiter = space)
            # Thickness (meters): (delimiter = space)
            # Unit Dip (aka tilt) (degrees): (delimiter = space)
            # Unit Dip Direction (aka Direction) (degrees): (delimiter = space)
            # Site Latitude (decimal degrees): (delimiter = space)
            # Site Longitude (decimal degrees): (delimiter = space)
            # Experiment Type (string): (delimiter = |)
            # Name of measurer (string): (delimiter = |)
            # Magnetometer name  (string): (delimiter = |)
            # Demagnetiser name  (string): (delimiter = |)
            # Specimen/Experiment Comment  (string): (delimiter = |)
            # Database version (integer): (delimiter = |)
            # Conversion Version (string): (delimiter = |)
            # Sample Volume (cc): (delimiter = |)
            # Sample Density  (kg/m^3): (delimiter = |)
            #
            #
            # BODY:
            # 1) Body includes 22 fields delimited by comma (',')
            # 2) Body ends with an "END" statment
            #
            # Body fields:
            # Treatment (aka field) (mT / deg C / 10-2 W): (delimiter = space)
            # Microwave Power (W) : (delimiter = space)
            # Microwave Time (s) : (delimiter = space)
            # X (nAm^2): (delimiter = space)
            # Y (nAm^2): (delimiter = space)
            # Z (nAm^2): (delimiter = space)
            # Mass g: (delimiter = space)
            # Applied field intensity (micro_T): (delimiter = space)
            # Applied field Dec (degrees): (delimiter = space)
            # Applied Field Inc (degrees): (delimiter = space)
            # Measurement Date (DD-MM-YYYY)  or (DD/MM/YYYY) #### CHECK !! ## (delimiter = |)
            # Measurement Time (HH:SS:MM) (delimiter = |)
            # Measurement Remark (string) (delimiter = |)
            # Step Number (integer) (delimiter = |)
            # Step Type (string) (Z/I/P/T/O/NRM) (delimiter = |)
            # Tristan Gain (integer) (delimiter = |)
            # Microwave Power Integral (W.s) (delimiter = |)
            # JR6 Error(percent %) (delimiter = |)
            # FiT Smm (?) (delimiter = |)
            # Utrecht Error (percent %) (delimiter = |)
            # AF Demag/Remag Peak Field (mT) (delimiter = |)
            # TH Demag/Remag Peak Temperature (deg C) (delimiter = |)
            # -------------------------------------------------------------


            #--------------------------------------
            # Important assumptions:
            # (1) The program checks if the same treatment appears more than once (a measurement is repeated twice).
            #       If yes, then it takes only the second one and ignores the first.
            # (2) –99 and 999 are codes for N/A
            # (3) The "treatment step" for Thermal Thellier experiment is taken from the "TH Demag/Remag Peak Temperature"
            # (4) The "treatment step" for Microwave Thellier experiment is taken from the "Step Number"
            # (5) As there might be contradiction between the expected treatment (i.e. Z,I,P,T,A assumed by the experiment type)
            #       and "Step Type" field due to typos or old file formats:
            #       The program concludes the expected treatment from the following:
            #       ("Experiment Type) + ("Step Number" or "TH Demag/Remag Peak Temperature") + (the order of the measurements).
            #       The conversion script will spit out a WARNING message in a case of contradiction.
            # (6) If the program finds AF demagnetization before the infield ot zerofield steps:
            #       then assumes that this is an AFD step domne before the experiment.
            # (7) The prgram ignores microwave fields (aka field,Microwave Power,Microwave Time) in Thermal experiments. And these fields will not be converted
            #     to MagIC.
            # (8) NRM step: NRM step is regonized either by "Applied field intensity"=0 and "Applied field Dec" =0 and "Applied Field Inc"=0
            #               or if "Step Type" = NRM
            #
            #
            #
            # -------------------------------------------------------------


            #--------------------------------------
            # Script was tested on the following protocols:
            # TH-PI-IZZI+ [November 2013, rshaar]
            # MW-PI-C++ [November 2013, rshaar]
            # MW-PI-IZZI+ ]November 2013, rshaar]
            #
            # Other protocols should be tested before use.
            #
            #
            #
            # -------------------------------------------------------------
            '''

        self.text_log.AppendText(TEXT)
        self.panel.SetSizer(self.sizer)



    # ===========================================
    # Convert to MagIC format
    # ===========================================

def convert(dir_path, meas_out="measurements.txt",
            spec_out="specimens.txt", samp_name_con=1, samp_num_chars=0,
            site_name_con=1, site_num_chars=0, location_name="", data_model_num=3):

    """
    # --------------------------------------
    # Read the file
    #
    # Livdb Database structure
    #
    # HEADER:
    # 1) First line is the header.
    #    The header includes 19 fields delimited by comma (',')
    #    Notice: space is not a delimiter !
    #    In the list below the delimiter is not used, and the conversion script assumes comma delimited file
    #
    # Header fields:
    # Sample code (string): (delimiter = space+)
    # Sample Dip (degrees): (delimiter = space)
    # Sample Dec (degrees): (delimiter = space)
    # Height (meters): (delimiter = space)
    # Position (no units): (delimiter = space)
    # Thickness (meters): (delimiter = space)
    # Unit Dip (aka tilt) (degrees): (delimiter = space)
    # Unit Dip Direction (aka Direction) (degrees): (delimiter = space)
    # Site Latitude (decimal degrees): (delimiter = space)
    # Site Longitude (decimal degrees): (delimiter = space)
    # Experiment Type (string): (delimiter = |)
    # Name of measurer (string): (delimiter = |)
    # Magnetometer name  (string): (delimiter = |)
    # Demagnetiser name  (string): (delimiter = |)
    # Specimen/Experiment Comment  (string): (delimiter = |)
    # Database version (integer): (delimiter = |)
    # Conversion Version (string): (delimiter = |)
    # Sample Volume (cc): (delimiter = |)
    # Sample Density  (kg/m^3): (delimiter = |)
    #
    #
    # BODY:
    # 1) Body includes 22 fields delimited by comma (',')
    # 2) Body ends with an "END" statment
    #
    # Body fields:
    # Treatment (aka field) (mT / deg C / 10-2 W): (delimiter = space)
    # Microwave Power (W) : (delimiter = space)
    # Microwave Time (s) : (delimiter = space)
    # X (nAm^2): (delimiter = space)
    # Y (nAm^2): (delimiter = space)
    # Z (nAm^2): (delimiter = space)
    # Mass g: (delimiter = space)
    # Applied field intensity (micro_T): (delimiter = space)
    # Applied field Dec (degrees): (delimiter = space)
    # Applied Field Inc (degrees): (delimiter = space)
    # Measurement Date (DD-MM-YYYY)  or (DD/MM/YYYY) #### CHECK !! ## (delimiter = |)
    # Measurement Time (HH:SS:MM) (delimiter = |)
    # Measurement Remark (string) (delimiter = |)
    # Step Number (integer) (delimiter = |)
    # Step Type (string) (Z/I/P/T/O/NRM) (delimiter = |)
    # Tristan Gain (integer) (delimiter = |)
    # Microwave Power Integral (W.s) (delimiter = |)
    # JR6 Error(percent %) (delimiter = |)
    # FiT Smm (?) (delimiter = |)
    # Utrecht Error (percent %) (delimiter = |)
    # AF Demag/Remag Peak Field (mT) (delimiter = |)
    # TH Demag/Remag Peak Temperature (deg C) (delimiter = |)
    # -------------------------------------------------------------

    # --------------------------------------
    # Importamt assumptions:
    # (1) The program checks if the same treatment appears more than once (a measurement is repeated twice).
    #       If yes, then it takes only the second one and ignores the first.
    # (2) –99 and 999 are codes for N/A
    # (3) The "treatment step" for Thermal Thellier experiment is taken from the "TH Demag/Remag Peak Temperature"
    # (4) The "treatment step" for Microwave Thellier experiment is taken from the "Step Number"
    # (5) As there might be contradiction between the expected treatment (i.e. Z,I,P,T,A assumed by the experiment type)
    #       and "Step Type" field due to typos or old file formats:
    #       The program concludes the expected treatment from the following:
    #       ("Experiment Type) + ("Step Number" or "TH Demag/Remag Peak Temperature") + (the order of the measurements).
    #       The conversion script will spit out a WARNING message in a case of contradiction.
    # (6) If the program finds AF demagnetization before the infield ot zerofield steps:
    #       then assumes that this is an AFD step domne before the experiment.
    # (7) The prgram ignores microwave fields (aka field,Microwave Power,Microwave Time) in Thermal experiments. And these fields will not be converted
    #     to MagIC.
    # (8) NRM step: NRM step is regonized either by "Applied field intensity"=0 and "Applied field Dec" =0 and "Applied Field Inc"=0
    #               or if "Step Type" = NRM
    #
    #
    #
    # -------------------------------------------------------------

    # --------------------------------------
    # Script was tested on the following protocols:
    # TH-PI-IZZI+ [November 2013, rshaar]
    # MW-PI-C++ [November 2013, rshaar]
    # MW-PI-IZZI+ ]November 2013, rshaar]
    #
    # Other protocols should be tested before use.
    #
    #
    #
    # -------------------------------------------------------------
    """

    if data_model_num == 2:
        loc_col = "er_location_name"
        site_col = "er_site_name"
        samp_col = "er_sample_name"
        spec_col = "er_specimen_name"
        citation_col = "er_citation_names"
        analyst_col = "er_analyst_mail_names"
        instrument_col = "magic_instrument_codes"
        quality_col = "measurement_flag"
        standard_col = "measurement_standard"
        step_col = "measurement_number"
        experiment_col = "magic_experiment_name"
        methods_col = "magic_method_codes"
        dec_col = "measurement_dec"
        inc_col = "measurement_inc"
        moment_col = "measurement_magn_moment"
        meas_temp_col = "measurement_temp"
        dc_field_col = "treatment_dc_field"
        dc_field_phi_col = "treatment_dc_field_phi"
        dc_field_theta_col = "treatment_dc_field_theta"
        mw_power_col = "treatment_mw_power"
        mw_time_col = "treatment_mw_time"
        mw_integral_col = "treatment_mw_integral"
        meas_descr_col = "measurement_description"
        treat_temp_col = "treatment_temp"
        ac_field_col = "treatment_ac_field"
        spec_type_col = "specimen_type"
        spec_lithology_col = "specimen_lithology"
        spec_class_col = "specimen_class"
        spec_dip_col = "specimen_dip"
        spec_azimuth_col = "specimen_azimuth"
        spec_height_col = "specimen_height"
        spec_descr_col = "specimen_description"
        spec_vol_col = "specimen_volume"
        spec_density_col = "specimen_density"
        date_col = "measurement_date"
        if meas_out == "measurements.txt":
            meas_out = "magic_measurements.txt"
        if spec_out == "specimens.txt":
            spec_out = "er_specimens.txt"
        meas_type = "magic_measurements"
        spec_type = "er_specimens"
    else:
        loc_col = "location"
        site_col = "site"
        samp_col = "sample"
        spec_col = "specimen"
        citation_col = "citations"
        analyst_col = "analysts"
        instrument_col = "instrument_codes"
        quality_col = "quality"
        standard_col = "standard"
        step_col = "treat_step_num"
        experiment_col = "experiment"
        methods_col = "method_codes"
        dec_col = "dir_dec"
        inc_col = "dir_inc"
        moment_col = "magn_moment"
        meas_temp_col = "meas_temp"
        dc_field_col = "treat_dc_field"
        dc_field_phi_col = "treat_dc_field_phi"
        dc_field_theta_col = "treat_dc_field_theta"
        mw_power_col = "treat_mw_power"
        mw_time_col = "treat_mw_time"
        mw_integral_col = "treat_mw_integral"
        meas_descr_col = "description"
        treat_temp_col = "treat_temp"
        ac_field_col = "treat_ac_field"
        spec_type_col = "geologic_types"
        spec_lithology_col = "lithologies"
        spec_class_col = "geologic_classes"
        spec_dip_col = "dip"
        spec_azimuth_col = "azimuth"
        spec_height_col = "height"
        spec_descr_col = "description"
        spec_vol_col = "volume"
        spec_density_col = "density"
        date_col = "timestamp"
        meas_type = "measurements"
        spec_type = "specimens"

    specimen_headers = []
    MagRecs = []
    measurement_headers = []
    ErRecs = []


    # -----------------------------------
    # Read file and sort data by specimen
    # -----------------------------------

    for files in os.listdir(dir_path):
        if files.endswith(".livdb") or files.endswith(".livdb.csv") or files.endswith(".csv"):
            fname = os.path.join(dir_path, files)
            print("Open file: ", fname)
            fin = open(fname, 'r')
            Data = {}
            header_codes = ['Sample code', 'Sample Dip', 'Sample Dec', 'Height', 'Position', 'Thickness', 'Unit Dip', 'Unit Dip Direction', 'Site Latitude',
                            'Site Longitude', 'Experiment Type', 'Name of measurer', 'Magnetometer name', 'Demagnetiser name', 'Specimen/Experiment Comment',
                            'Database version', 'Conversion Version', 'Sample Volume', 'Sample Density']

            meas_codes = ['Treatment (aka field)', 'Microwave Power', 'Microwave Time', 'moment_X', 'moment_Y', 'moment_Z', 'Mass', 'Applied field Intensity', 'Applied field Dec',
                          'Applied field Inc', 'Measurement Date', 'Measurement Time', 'Measurement Remark', 'Step Number', 'Step Type', 'Tristan Gain', 'Microwave Power Integral',
                          'JR6 Error', 'FiT Smm', 'Utrecht Error', 'AF Demag/Remag Peak Field', 'TH Demag/Remag Peak Temperature']

            line_number = 0
            continue_reading = True
            while continue_reading:
                # first line is the header
                this_specimen = True
                while this_specimen == True:
                    line = fin.readline()
                    line_number += 1
                    if not line:
                        continue_reading = False
                        break

                    # -------------------------------
                    # Read infromation from Header and body
                    # The data is stored in a dictionary:
                    # Data[specimen][Experiment_Type]['header_data']=tmp_header_data  --> a dictionary with header data
                    # Data[specimen][Experiment_Type]['meas_data']=[dict1, dict2, ...] --> a list of dictionaries with measurement data
                    # -------------------------------

                    header = line.strip('\n').split(",")
                    #header=str(this_line[0]).split()+ this_line[1:-1]

                    # header consists of  fields seperated by spaces and "|"

            # if len (header) > 15:
            ##                this_line_data[14:]=" ".join(this_line_data[14:])
            # del(this_line_data[15:])

                    # warning if missing info.

                    if len(header) < 19:
                        print("missing data in header.Line %i" %
                              line_number)
                        print(header)

                    # read header and sort in a dictionary
                    tmp_header_data = {}

                    for i in range(len(header_codes)):
                        tmp_header_data[header_codes[i]] = header[i]
                    specimen = tmp_header_data['Sample code']
                    Experiment_Type = tmp_header_data['Experiment Type']

                    if specimen not in list(Data.keys()):
                        Data[specimen] = {}
                    if Experiment_Type in list(Data[specimen].keys()):
                        print(
                            "-E- specimen %s has duplicate Experimental type %s. check it!" % (specimen, Experiment_Type))

                    Data[specimen][Experiment_Type] = {}
                    Data[specimen][Experiment_Type]['header_data'] = tmp_header_data
                    Data[specimen][Experiment_Type]['meas_data'] = []

                    # ---------------------------------------------------
                    # Read infromation from body and sort in dictonaries
                    # ---------------------------------------------------

                    while this_specimen:
                        line = fin.readline()
                        line_number += 1
                        # each specimen ends with "END" statement
                        if "END" in line:
                            this_specimen = False
                            break
                        # this_line=line.strip('\n').split("|")
                        #this_line_data=str(this_line[0]).split()+ this_line[1:-1]
                        this_line_data = line.strip('\n').split(",")
                        if len(this_line_data) < 22:
                            print("missing data in Line %i" %
                                  line_number)
                            print(this_line_data)
                            all_null = True
                            for i in this_line_data:
                                if i:
                                    all_null = False
                            if all_null:
                                this_specimen = False
                                break

                        tmp_data = {}
                        for i in range(len(this_line_data)):
                            tmp_data[meas_codes[i]] = this_line_data[i]
                        Data[specimen][Experiment_Type]['meas_data'].append(
                            tmp_data)

            # -----------------------------------
            # Convert to MagIC
            # -----------------------------------

            specimens_list = list(Data.keys())
            specimens_list.sort()
            for specimen in specimens_list:
                Experiment_Types_list = list(Data[specimen].keys())
                Experiment_Types_list.sort()
                for Experiment_Type in Experiment_Types_list:

                    # -----------------------------------
                    # Assuming that the first line is NRM always
                    # MW-PI-OT+:
                    #  Microwave Thellier Thellier protocol
                    # MW-PI-P:
                    #  Perpendicular mathod
                    #  demagnetizations until overprint is removed
                    #  then remagnetization perpendicular to the remaining NRM direction
                    # -----------------------------------

                    supported_experiments = ['MW-PI-OT+', 'MW-PI-P', 'MW-PI-C', 'MW-PI-C+', 'MW-PI-C++', 'MW-PI-IZZI', 'MW-PI-IZZI+', 'MW-PI-IZZI++', 'MW-PI-A', 'MW-PI-A+',
                                             'TH-PI-OT+', 'TH-PI-P', 'TH-PI-C', 'TH-PI-C+', 'TH-PI-C++', 'TH-PI-IZZI', 'TH-PI-IZZI+', 'TH-PI-IZZI++', 'TH-PI-A', 'TH-PI-A+',
                                             'TH-D', 'AF-D']
                    if Experiment_Type in supported_experiments:

                        header_line = Data[specimen][Experiment_Type]['header_data']
                        experiment_treatments, lab_treatments = [], []
                        measurement_running_number = 0
                        for i in range(len(Data[specimen][Experiment_Type]['meas_data'])):
                            meas_line = Data[specimen][Experiment_Type]['meas_data'][i]

                            # check if the same treatment appears more than once. If yes, assuming that the measurements is repeated twice,
                            # ignore the first, and take only the second one

                            if i < (len(Data[specimen][Experiment_Type]['meas_data'])-2):
                                Repeating_measurements = True
                                for key in ["Treatment (aka field)", "Microwave Power", "Microwave Time", "AF Demag/Remag Peak Field", "Applied field Intensity",
                                            "Applied field Dec", "Applied field Inc", "Step Type", "TH Demag/Remag Peak Temperature"]:
                                    if Data[specimen][Experiment_Type]['meas_data'][i][key] != Data[specimen][Experiment_Type]['meas_data'][i+1][key]:
                                        Repeating_measurements = False
                                if Repeating_measurements == True:
                                    print("Found a repeating measurement at line %i, sample %s. taking the last one" % (
                                        i, specimen))
                                    continue
                            # ------------------

                            MagRec = {}
                            # header_data
                            MagRec[citation_col] = "This study"
                            MagRec[spec_col] = header_line['Sample code']
                            MagRec[samp_col] = get_sample_name(
                                MagRec[spec_col], [samp_name_con, samp_num_chars])
                            MagRec[site_col] = get_site_name(
                                MagRec[samp_col], [site_name_con, site_num_chars])
                            MagRec[loc_col] = location_name
                            MagRec[analyst_col] = header_line['Name of measurer']
                            MagRec[instrument_col] = header_line['Magnetometer name'] + \
                                ":"+header_line['Demagnetiser name']

                            # meas data
                            MagRec[quality_col] = 'g'
                            MagRec[standard_col] = 'u'
                            MagRec[step_col] = "%i" % measurement_running_number
                            CART = array([1e-9*float(meas_line['moment_X']), 1e-9*float(
                                meas_line['moment_Y']), 1e-9*float(meas_line['moment_Z'])])  # Am^2
                            DIR = pmag.cart2dir(CART)
                            MagRec[dec_col] = "%.2f" % DIR[0]
                            MagRec[inc_col] = "%.2f" % DIR[1]
                            MagRec[moment_col] = '%10.3e' % (
                                math.sqrt(sum(CART**2)))
                            # room temp in kelvin
                            MagRec[meas_temp_col] = '273.'

                            # Date and time
                            if "-" in meas_line['Measurement Date']:
                                date = meas_line['Measurement Date'].strip(
                                    "\"").split('-')
                            elif "/" in meas_line['Measurement Date']:
                                date = meas_line['Measurement Date'].strip(
                                    "\"").split('/')
                            else:
                                print(
                                    "-E- ERROR: line no. %i please use one of the following convention for date: MM-DD-YYYY or MM/DD/YYYY" % i)
                            yyyy = date[2]
                            dd = date[1]
                            mm = date[0]
                            hour = meas_line['Measurement Time'].strip(
                                "\"")
                            MagRec[date_col] = yyyy + \
                                ':'+mm+":"+dd+":"+hour

                            # lab field data: distinguish between PI experiments to AF/Thermal
                            if Experiment_Type == "TH-D" or Experiment_Type == "AF-D":
                                MagRec[dc_field_col] = '0'
                                MagRec[dc_field_phi_col] = '0'
                                MagRec[dc_field_theta_col] = '0'
                            else:
                                labfield = float(
                                    meas_line['Applied field Intensity'])*1e-6
                                MagRec[dc_field_col] = '%8.3e' % (
                                    labfield)
                                MagRec[dc_field_phi_col] = meas_line['Applied field Dec']
                                MagRec[dc_field_theta_col] = meas_line['Applied field Inc']

                            # treatment (MW or Thermal)
                            if "MW-" in Experiment_Type:
                                MagRec[mw_power_col] = meas_line['Microwave Power']
                                MagRec[mw_time_col] = meas_line['Microwave Time']
                                MagRec[mw_integral_col] = meas_line['Microwave Power Integral']
                                MagRec[meas_descr_col] = "Step Type"+"-" + \
                                    meas_line['Step Type']+":Step Number-" + \
                                    "%i" % int(
                                        meas_line['Step Number'])
                                # Ron CHECK !!
                                treatment = meas_line['Step Number']
                            elif "TH-" in Experiment_Type:
                                MagRec[treat_temp_col] = "%.2f" % (
                                    float(meas_line['TH Demag/Remag Peak Temperature'])+273)
                                treatment = meas_line['TH Demag/Remag Peak Temperature']
                            elif "AF-" in Experiment_Type:
                                MagRec[ac_field_col] = '%8.3e' % (
                                    float(meas_line['TH Demag/Remag Peak Temperature'])*1e-3)  # peak field in tesla
                                treatment = meas_line['AF Demag/Remag Peak Field']

                            # -----------------------------------
                            # notice future problems with the first line because "NRM" will not be in the Step Type field
                            # -----------------------------------
                            lab_treatment = ""
                            if len(experiment_treatments) == 0:
                                if float(MagRec[dc_field_col]) == 0 and float(MagRec[dc_field_phi_col]) == 0 and MagRec[dc_field_theta_col] == 0:
                                    lab_treatment = "LT-NO"
                                    experiment_treatments.append('0')
                                    IZorZI = ""
                                elif "NRM" in meas_line['Step Type']:
                                    lab_treatment = "LT-NO"
                                    experiment_treatments.append(
                                        MagRec[dc_field_col])
                                    IZorZI = ""

                            # -----------------------------------
                            # Detect AFD in the first lines of Thelier Type experiments
                            # -----------------------------------

                            no_treatments_yet = True
                            for t in experiment_treatments:
                                t = float(t.strip())
                                if t > 50:
                                    no_treatments_yet=False
                            if no_treatments_yet:
                                if meas_line['AF Demag/Remag Peak Field'] != "" and \
                                   float(meas_line['AF Demag/Remag Peak Field']) != 999 and \
                                   float(meas_line['AF Demag/Remag Peak Field']) != -99 and \
                                   float(meas_line['AF Demag/Remag Peak Field']) != 0:
                                    lab_treatment = "LT-AF-Z"
                                    MagRec[ac_field_col] = '%8.3e' % (
                                        float(meas_line['AF Demag/Remag Peak Field'])*1e-3)  # peak field in tesla

                            # -----------------------------------
                            # Thellier-Thellier protocol:
                            # -----------------------------------

                            if Experiment_Type in ['MW-PI-OT', 'MW-PI-OT+', 'TH-PI-OT', 'TH-PI-OT+']:
                                if Experiment_Type == 'MW-PI-OT+':
                                    lab_protocols_string = "LP-PI-M:LP-PI-II:LP-PI-M-II:LP-PI-ALT-PMRM"
                                elif Experiment_Type == 'MW-PI-OT':
                                    lab_protocols_string = "LP-PI-M:LP-PI-II:LP-PI-M-II"
                                # first line
                                if len(experiment_treatments) == 0 and lab_treatment == "":
                                    lab_treatment = "LT-NO"
                                # PMRM check
                                elif labfield != 0 and float(treatment) < float(experiment_treatments[-1]):
                                    lab_treatment = "LT-PMRM-I"
                                    if Experiment_Type != 'MW-PI-OT+':
                                        print("-W- WARNING sample %s: Check Experiment_Type ! it is %s, but a pTRM check is found."
                                              % (MagRec[spec_col], Experiment_Type))
                                else:
                                    lab_treatment = "LT-M-I"
                                # experiment_treatments.append(treatment)

                            # -----------------------------------
                            # Coe/Aitken/IZZI protocols:
                            # Coe: N/ZI/.../ZPI/.../ZIT/.../ZPIT/
                            # Aitken: N/IZ/.../IZP/.../ITZ/.../ITZP/
                            # IZZI: N/IZ/ZI/../ZPI/...ITZ/.../ZPIT/.../ITZP/...
                            # -----------------------------------

                            if Experiment_Type in ['MW-PI-C', 'MW-PI-C+', 'MW-PI-C++', 'MW-PI-IZZI', 'MW-PI-IZZI+', 'MW-PI-IZZI++', 'MW-PI-A', 'MW-PI-A+',
                                                   'TH-PI-C', 'TH-PI-C+', 'TH-PI-C++', 'TH-PI-IZZI', 'TH-PI-IZZI+', 'TH-PI-IZZI++', 'TH-PI-A', 'TH-PI-A+']:

                                if Experiment_Type == 'MW-PI-C++':
                                    lab_protocols_string = "LP-PI-M:LP-PI-ZI:LP-PI-M-ZI:LP-PI-ALT-PMRM:LP-PI-BT-MD"
                                elif Experiment_Type == 'MW-PI-C+':
                                    lab_protocols_string = "LP-PI-M:LP-PI-ZI:LP-PI-M-ZI:LP-PI-ALT-PMRM"
                                elif Experiment_Type == 'MW-PI-C':
                                    lab_protocols_string = "LP-PI-M:LP-PI-ZI:LP-PI-M-ZI"
                                elif Experiment_Type == 'MW-PI-IZZI++':
                                    lab_protocols_string = "LP-PI-M:LP-PI-BT-IZZI:LP-PI-ALT-PMRM:LP-PI-BT-MD"
                                elif Experiment_Type == 'MW-PI-IZZI+':
                                    lab_protocols_string = "LP-PI-M:LP-PI-BT-IZZI:LP-PI-ALT-PMRM"
                                elif Experiment_Type == 'MW-PI-IZZI':
                                    lab_protocols_string = "LP-PI-M:LP-PI-BT-IZZI"
                                elif Experiment_Type == 'MW-PI-A+':
                                    lab_protocols_string = "LP-PI-M:LP-PI-IZ:LP-PI-M-IZ:LP-PI-ALT-PMRM"
                                elif Experiment_Type == 'MW-PI-A':
                                    lab_protocols_string = "LP-PI-M:LP-PI-IZ:LP-PI-M-IZ"
                                elif Experiment_Type == 'TH-PI-C++':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-ZI:LP-PI-TRM-ZI:LP-PI-ALT-PTRM:LP-PI-BT-MD"
                                elif Experiment_Type == 'TH-PI-C+':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-ZI:LP-PI-TRM-ZI:LP-PI-ALT-PTRM"
                                elif Experiment_Type == 'TH-PI-C':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-ZI:LP-PI-TRM-ZI"
                                elif Experiment_Type == 'TH-PI-IZZI++':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-BT-IZZI:LP-PI-ALT-PTRM:LP-PI-BT-MD"
                                elif Experiment_Type == 'TH-PI-IZZI+':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-BT-IZZI:LP-PI-ALT-PTRM"
                                elif Experiment_Type == 'TH-PI-IZZI':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-BT-IZZI"
                                elif Experiment_Type == 'TH-PI-A+':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-IZ:LP-PI-TRM-IZ:LP-PI-ALT-PMRM"
                                elif Experiment_Type == 'TH-PI-A':
                                    lab_protocols_string = "LP-PI-TRM:LP-PI-IZ:LP-PI-TRM-IZ"
                                else:
                                    "-E- ERROR: cant understand protocol type"

                                if "TH-PI" in Experiment_Type:
                                    TH = True
                                    MW = False
                                else:
                                    TH = False
                                    MW = True

                                # -------------------------------------
                                # Special treatment for first line
                                # -------------------------------------

                                if len(experiment_treatments) == 0:
                                    if lab_treatment == "":
                                        lab_treatment = "LT-NO"
                                    elif float(lab_treatment) < 50:
                                        lab_treatment = "LT-NO"
                                    else:
                                        pass

                                # -------------------------------------
                                # Assigning Lab Treatment
                                # -------------------------------------

                                    # a flag for the current state (Z,I,ZP,T)
                                    IZorZI = ""
                                    # Coe:
                                else:
                                    if float(treatment) != 0:
                                        if labfield == 0 and treatment not in experiment_treatments:
                                            lab_treatment = "LT-M-Z"*MW + "LT-T-Z"*TH
                                            IZorZI = "Z"

                                        elif labfield == 0 and treatment in experiment_treatments:
                                            if IZorZI == 'I':
                                                lab_treatment = "LT-M-Z"*MW + "LT-T-Z"*TH
                                                IZorZI = ""
                                            else:
                                                lab_treatment = "LT-PMRM-MD"*MW + "LT-PTRM-MD"*TH

                                        elif labfield != 0 and treatment not in experiment_treatments:
                                            lab_treatment = "LT-M-I"*MW + "LT-T-I"*TH
                                            IZorZI = "I"

                                        elif labfield != 0 and treatment in experiment_treatments:
                                            # if IZorZI=='Z' or IZorZI=='':

                                            prev_treatment = treatment
                                            # print lab_treatments,"lab_treatments"
                                            # print experiment_treatments,"experiment_treatments"
                                            if len(experiment_treatments) > 2 and len(lab_treatments) > 2:
                                                for j in range(len(lab_treatments)-1, 0, -1):
                                                    if "LT-PTRM-I" in lab_treatments[j] or "LT-PMRM-I" in lab_treatments[j]:
                                                        continue
                                                    prev_treatment = experiment_treatments[j]
                                                    break
                                            # print "prev_treatment",prev_treatment
                                            # print "treatment",treatment

                                            if float(treatment) < float(prev_treatment):
                                                lab_treatment = "LT-PMRM-I"*MW + "LT-PTRM-I"*TH
                                                IZorZI == ''
                                            else:
                                                lab_treatment = "LT-M-I"*MW + "LT-T-I"*TH
                                                IZorZI = ""

                                        else:
                                            print("-E- ERROR. specimen %s. Cant relate step %s to the protocol" %
                                                  (MagRec[spec_col], treatment))

                                # check Step Type in the file and the deduced step from the program
                                if ((lab_treatment == "LT-M-I" or lab_treatment == "LT-T-I") and meas_line['Step Type'] != "I") or \
                                   ((lab_treatment == "LT-M-Z" or lab_treatment == "LT-T-Z") and meas_line['Step Type'] != "Z") or \
                                   ((lab_treatment == "LT-PMRM-I" or lab_treatment == "LT-PTRM-I") and meas_line['Step Type'] != "P") or \
                                   ((lab_treatment == "LT-PMRM-MD" or lab_treatment == "LT-PTRM-MD") and meas_line['Step Type'] != "T"):
                                    print("-W- WARNING sample %s treatment=%s. Step Type is %s but the program assumes %s"
                                          % (MagRec[spec_col], treatment, meas_line['Step Type'], lab_treatment))

                                # experiment_treatments.append(treatment)
                                lab_treatments.append(lab_treatment)
                            # -----------------------------------
                            # Perpendicular method: MW-PI-P :
                            # -----------------------------------

                            if Experiment_Type == 'MW-PI-P':
                                lab_protocols_string = "LP-PI-M:LP-PI-M-PERP"
                                if len(experiment_treatments) == 0:
                                    lab_treatment = "LT-NO"
                                if labfield == 0:
                                    lab_treatment = "LT-M-Z"
                                else:
                                    lab_treatment = "LT-M-I:LT-NRM-PERP"

                                # experiment_treatments.append(treatment)

                            # -----------------------------------
                            # MW demagnetization
                            # -----------------------------------

                            if Experiment_Type in ['MW-D']:
                                # first line
                                if len(experiment_treatments) == 0 and lab_treatment == "":
                                    if float(treatment) == 0:
                                        lab_treatment = "LT-NO"
                                    else:
                                        lab_treatment = "LT-M-Z"
                                else:
                                    lab_protocols_string = "LP-DIR-M"
                                    lab_treatment = "LT-M-Z"

                                # experiment_treatments.append(treatment)

                            # -----------------------------------
                            # Thermal demagnetization
                            # -----------------------------------

                            if Experiment_Type in ['TH-D']:
                                # first line
                                if len(experiment_treatments) == 0 and lab_treatment == "":
                                    if float(treatment) == 0:
                                        lab_treatment = "LT-NO"
                                    else:
                                        lab_treatment = "LT-T-Z"
                                else:
                                    lab_protocols_string = "LP-DIR-T"
                                    lab_treatment = "LT-T-Z"

                                # experiment_treatments.append(treatment)

                            # -----------------------------------
                            # AF demagnetization
                            # -----------------------------------

                            if Experiment_Type in ['AF-D']:
                                # first line
                                if len(experiment_treatments) == 0 and lab_treatment == "":
                                    if float(treatment) == 0:
                                        lab_treatment = "LT-NO"
                                    else:
                                        lab_treatment = "LT-AF-Z"
                                else:
                                    lab_protocols_string = "LP-DIR-AF"
                                    lab_treatment = "LT-AF-Z"

                            experiment_treatments.append(treatment)

                            # -----------------------------------

                            MagRec[methods_col] = lab_treatment + \
                                ":"+lab_protocols_string
                            MagRec[methods_col] = MagRec[methods_col].strip(':')
                            MagRec[experiment_col] = specimen + \
                                ":"+lab_protocols_string
                            if data_model_num == 3:
                                MagRec['measurement'] = MagRec[experiment_col] + "_" + MagRec[step_col]
                            MagRecs.append(MagRec)
                            measurement_running_number += 1
                            headers = list(MagRec.keys())
                            for key in headers:
                                if key not in measurement_headers:
                                    measurement_headers.append(
                                        key)

                    else:
                        # print "experiment format",Experiment_Type," is not supported yet. sorry.."
                        print(
                            "livdb.py does not support this experiment type yet.please contact Ron Shaar at rshaar@ucsd.edu")

            # -----------------------------------
            # Convert Headers data to specimens
            # -----------------------------------

            for specimen in specimens_list:
                #print(specimen)
                Experiment_Types_list = list(Data[specimen].keys())
                Experiment_Types_list.sort()
                for Experiment_Type in Experiment_Types_list:
                    #print(Experiment_Type)
                    if Experiment_Type in supported_experiments:
                        header_line = Data[specimen][Experiment_Type]['header_data']
                        meas_first_line = Data[specimen][Experiment_Type]['meas_data'][0]
                        ErRec = {}
                        ErRec[citation_col] = "This study"
                        ErRec[spec_col] = header_line["Sample code"]
                        ErRec[samp_col] = get_sample_name(
                            MagRec[spec_col], [samp_name_con, samp_num_chars])
                        ErRec[site_col] = get_site_name(
                            MagRec[samp_col], [site_name_con, site_num_chars])
                        ErRec[loc_col] = location_name

                        ErRec[spec_type_col] = "Not Specified"
                        ErRec[spec_lithology_col] = "Not Specified"
                        ErRec[spec_class_col] = "Not Specified"

                        ErRec[spec_dip_col] = header_line['Sample Dip']
                        if float(ErRec[spec_dip_col]) == 99:
                            ErRec[spec_dip_col] = ""
                        ErRec[spec_azimuth_col] = header_line['Sample Dec']
                        if float(ErRec[spec_azimuth_col]) == 999:
                            ErRec[spec_azimuth_col] = ""
                        ErRec[spec_height_col] = header_line['Height']
                        ErRec[spec_descr_col] = header_line['Specimen/Experiment Comment']
                        try:
                            ErRec[spec_vol_col] = "%f" % float(
                                header_line['Sample Volume'])*1e-6
                        except:
                            ErRec[spec_vol_col] = ""

                        ErRec[spec_density_col] = header_line['Sample Density']

                        ErRecs.append(ErRec)
                        headers = list(ErRec.keys())
                        for key in headers:
                            if key not in specimen_headers:
                                specimen_headers.append(key)

    # -------------------------------------------
    #  magic_measurements.txt
    # -------------------------------------------

    fout = open(meas_out, 'w')
    fout.write("tab\t{}\n".format(meas_type))
    header_string = ""
    for i in range(len(measurement_headers)):
        header_string = header_string+measurement_headers[i]+"\t"
    fout.write(header_string[:-1]+"\n")

    for MagRec in MagRecs:
        line_string = ""
        for i in range(len(measurement_headers)):
            if measurement_headers[i] in list(MagRec.keys()):
                line_string = line_string + \
                    MagRec[measurement_headers[i]]+"\t"
            else:
                line_string = line_string+""+"\t"

        fout.write(line_string[:-1]+"\n")

    # -------------------------------------------
    #  er_specimens.txt
    # -------------------------------------------

    fout = open(spec_out, 'w')
    fout.write("tab\t{}\n".format(spec_type))
    header_string = ""
    for i in range(len(specimen_headers)):
        header_string = header_string+specimen_headers[i]+"\t"
    fout.write(header_string[:-1]+"\n")

    for ErRec in ErRecs:
        line_string = ""
        for i in range(len(specimen_headers)):
            if specimen_headers[i] in list(ErRec.keys()):
                line_string = line_string + \
                    ErRec[specimen_headers[i]]+"\t"
            else:
                line_string = line_string+"\t"

        fout.write(line_string[:-1]+"\n")

    # -------------------------------------------

def get_sample_name(specimen, sample_naming_convention):
    if sample_naming_convention[0] == "sample=specimen":
        sample = specimen
    elif sample_naming_convention[0] == "no. of terminate characters":
        n = int(sample_naming_convention[1])*-1
        sample = specimen[:n]
    elif sample_naming_convention[0] == "character delimited":
        d = sample_naming_convention[1]
        sample_splitted = specimen.split(d)
        if len(sample_splitted) == 1:
            sample = sample_splitted[0]
        else:
            sample = d.join(sample_splitted[:-1])
    return sample

def get_site_name(sample, site_naming_convention):
    if site_naming_convention[0] == "site=sample":
        site = sample
    elif site_naming_convention[0] == "no. of terminate characters":
        n = int(site_naming_convention[1])*-1
        site = sample[:n]
    elif site_naming_convention[0] == "character delimited":
        d = site_naming_convention[1]
        site_splitted = sample.split(d)
        if len(site_splitted == 1):
            site = site_splitted[0]
        else:
            site = d.join(site_splitted[:-1])

    return site



"""
NAME
    livdb_magic.py

DESCRIPTION
    converts Livdb format files to magic_measurements format files


"""


def main():
    if '-h' in sys.argv:
        print("Convert Livdb files to MagIC format")
        sys.exit()
    app = wx.App()
    app.frame = convert_livdb_files_to_MagIC("./")
    app.frame.Show()
    app.frame.Center()
    app.MainLoop()


if __name__ == '__main__':
    main()


# main()