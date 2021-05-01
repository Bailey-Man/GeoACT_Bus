# import
import json
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

sys.path.insert(0, 'src')
from bus import bus_sim
from infection import return_aerosol_transmission_rate

def load_parameters_av(filepath):
    '''
    Loads input and output directories
    '''
    try:
        with open(filepath) as fp:
            parameter = json.load(fp)
    except:
        try:
            with open('../' + filepath) as fp:
                parameter = json.load(fp)
        except:
            with open('../../' + filepath) as fp:
                parameter = json.load(fp)
    return parameter



class user_viz():
    def __init__(self, parent=None):
        super(user_viz, self).__init__()
        # separate input params
        self.input_params = load_parameters_av(filepath='results/default_data_.json')
        self.trip_length = self.input_params["trip_length"]
        self.students_var = self.input_params["number_students"]
        self.mask_var = self.input_params["mask_wearing_percent"]
        self.window_var = self.input_params["windows"]
        self.number_simulations = self.input_params["number_simulations"]

        self.input_params2 = load_parameters_av(filepath='results/aerosol_data_.json')
        self.mask_eff = self.input_params2["mask_passage_prob"]
        self.seat_var = self.input_params["seating_choice"]
        self.bus_trips = []

        # bus dimensions
        # width and height are relatively standard: ergo area is 2.3 * L
        self.bus_length = self.input_params["bus_length"]
        self.floor_area = self.bus_length * 2.3 # Sq M. (TODO: convert to units?)


        # functions
        self.relative_airflow = 'placeholder'

    def load_parameters(self, filepath):
        '''
        Loads seating from input directories
        '''
        # print(os.getcwd(), 'av_cwd')
        try:
            with open(filepath) as fp:
                parameter = json.load(fp)
        except:
            try:
                with open('../' + filepath) as fp:
                    parameter = json.load(fp)
            except:
                with open('../../' + filepath) as fp:
                    parameter = json.load(fp)

        return parameter

    def generate_bus_seating(self):
        '''
        based on full vs zigzag vs edge
        based on number of students
        '''
        # get seating type:
        temp = self.seat_var
        if temp == "Full Occupancy":
            seat_dict = self.load_parameters('config/f_seating_full.json')
        else:
            if temp == "Window Seats Only":
                seat_dict = self.load_parameters('config/f_seating_half_edge.json')
            else:
                seat_dict = self.load_parameters('config/f_seating_half_zig.json')
        # evaluate temp based on # students
        num_kids = self.students_var
        temp_dict = {}
        for i in range(int(num_kids)):
            temp_dict[str(i)] = seat_dict[str(i)]
        # print(temp)
        # print(temp_dict)
        return temp_dict

    def plot_bus_seating(self):
        '''
        plot avg based on temp dict

        TODO: background of bus
        '''
        t_dict = self.generate_bus_seating()
        x_arr = []
        y_arr = []
        # print('bus_seat_figure')
        plt.figure(figsize=(2,2))
        plt.gcf().set_size_inches(2,2)
        # plt.gcf().set_size_inches(2,2)
        for i in t_dict.items():
            x_arr.append(i[1][1])
            y_arr.append(i[1][0])
        plt.scatter(x=x_arr, y=y_arr)
        # plt.axis('off') # set axis to be blank
        # plt.show()

        plt.savefig('results/seating_plot.png', dpi=300)
        print('plot seating complete!')

        return

    def conc_heat(self):
        '''
        average over model runs: out_matrix averages
        '''
        bus_seating = self.generate_bus_seating()
        bus_trip, conc_array, out_mat, chance_nonzero = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var) # replace default with selected
        # print('conc_heat_figure')
        # plt.figure(figsize=(5,4))
        plt.matshow(out_mat, cmap="OrRd", norm=mpl.colors.LogNorm())
        plt.gcf().set_size_inches(2,2)
        plt.savefig('results/relative_airflow.png', dpi=300)
        print('relative airflow complete!')
        # plt.show()

        return
    # function to run model with user input
    def model_run(self):
        '''
        '''

        # run bus model
        bus_seating = self.generate_bus_seating()
        bus_trip, conc_array, out_mat, chance_nonzero = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var) # replace default with selected
        self.chance_nonzero = chance_nonzero
        print(chance_nonzero, 'more than none?')
        self.conc_array = conc_array
        self.bus_trips.append(bus_trip)
        # print('model_run start')
        plt.figure(figsize=(5,4))#, dpi=300)
        plt.gcf().set_size_inches(5,4)
        # plt.gcf().set_size_inches(5,4)
        # ax = plt.gca()
        pd.Series(bus_trip).plot.kde()
        plt.title('Density estimation of exposure')
        # plt.xlim(0, .004)
        #
        # # set x ticks
        # temp_x = np.array([i * 5 for i in range(8)])
        # str_x = np.array([str(int / 100)+'%' for int in temp_x])
        # plt.xticks(np.arange(0, .004, .0005), str_x)
        # plt.ticklabel_format(axis="x", style="sci", scilimits=(0,0))

        plt.yticks(np.arange(0, 3500, 700), np.arange(0, 3500, 700) / 3500)


        # rescale y axis to be % based
        plt.xlabel('Likelihood of exposure to infectious dose of particles')
        plt.ylabel('Density estimation of probability of occurrence')
        plt.savefig('results/window_curve.png', dpi=300)
        # plt.show()
        print('model_run complete!')
