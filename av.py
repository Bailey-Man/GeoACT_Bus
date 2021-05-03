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
        # im = plt.imread('results/bus_img.png')
        # plt.imshow(im)
        plt.title('Approximate Seating Chart', fontsize=7)
        plt.xticks(np.array([1.2, 1.8, 2.2, 3.8, 4.2, 4.8]))
        plt.yticks(np.arange(-.5, 23.5, 1))
        plt.grid(True)
        # plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        plt.scatter(x=x_arr, y=y_arr)#, marker='_')
        plt.xticks(c='w')
        plt.yticks(c='w')
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
        # plt.subplots()
        # base = plt.gca().transData
        # fig = plt.subplots() # ????
        rot = mpl.transforms.Affine2D().rotate_deg(180)
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.matshow(out_mat, cmap="OrRd", norm=mpl.colors.LogNorm())
        plt.arrow(-2,24,0,-26, head_width=0.2, head_length=0.2, fc='k', ec='k')
        plt.gcf().set_size_inches(2,2)
        # plt.suptitle('Relative Airflow Heatmap', fontsize=7.5)
        plt.annotate(xy=(-1, -1), text='front', fontsize=5)
        plt.annotate(xy=(-1, 24), text='back', fontsize=5)
        plt.axis('off')


        ax2 = fig.add_subplot(1,2,2)
        ax2.matshow(out_mat, cmap="OrRd")#, norm=mpl.colors.LogNorm())
        plt.arrow(-2,24,0,-26, head_width=0.2, head_length=0.2, fc='k', ec='k')
        plt.gcf().set_size_inches(2,2)
        plt.suptitle('Relative Airflow Heatmap', fontsize=7.5)
        plt.annotate(xy=(-1, -1), text='front', fontsize=5)
        plt.annotate(xy=(-1, 24), text='back', fontsize=5)
        # log scale vs regular scale + 'be not afraid'
        plt.axis('off')
        fig.text(.1, .01, 'These heatmaps show relative airflow within the cabin \nof the bus in terms of its effect on concentration \nof COVID-19 Particles (averaged across 100 simulations)', fontsize=4)
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
        # print(chance_nonzero, 'more than none?')
        self.conc_array = conc_array
        self.bus_trips.append(bus_trip)
        # print('model_run start')
        plt.figure(figsize=(5,4))#, dpi=300)
        plt.gcf().set_size_inches(5,4)
        # plt.gcf().set_size_inches(5,4)
        # ax = plt.gca()
        pd.Series(bus_trip).plot.kde(lw=2, c='r')
        plt.title('Density estimation of exposure')
        # plt.xlim(0, .004)
        # print(plt.xticks())

        # set x ticks
        temp_x = np.array(plt.xticks()[0])
        str_x = np.array([str(round(int * 100, 2))+'%' for int in temp_x])
        print(str_x)
        plt.xticks(temp_x, str_x)

        plt.ticklabel_format(axis="x")#, style="sci", scilimits=(0,0))

        plt.yticks(np.arange(0, 3500, 700), np.arange(0, 3500, 700) / 3500)


        # rescale y axis to be % based
        plt.xlabel('Likelihood of exposure to infectious dose of particles                         ')
        plt.ylabel('Density estimation of probability of occurrence')
        plt.savefig('results/window_curve.png', dpi=300)
        # plt.show()
        print('model_run complete!')
