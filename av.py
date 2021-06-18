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
        self.window_var = self.input_params["window_var"]
        # print(self.window_var, 'what')
        self.number_simulations = self.input_params["number_simulations"]

        self.input_params2 = load_parameters_av(filepath='results/aerosol_data_.json')
        self.mask_eff = self.input_params2["mask_passage_prob"]
        self.seat_var = self.input_params["seating_choice"]
        self.bus_out_arrays = []

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
        # print(temp, type(temp), 'temp')
        if temp == "full":
            seat_dict = self.load_parameters('config/f_seating_full.json')
        else:
            if temp == "window":
                seat_dict = self.load_parameters('config/f_seating_half_edge.json')
            elif temp == "zigzag":
                seat_dict = self.load_parameters('config/f_seating_half_zig.json')
            else:
                print('error temp bad')
        # evaluate temp based on # students
        num_kids = self.students_var
        # print(num_kids, 'num_kids')
        temp_dict = {}
        for i in range(int(num_kids)):
            temp_dict[str(i)] = seat_dict[str(i)]
        # print(temp)
        # print(temp_dict, 'temp')
        return temp_dict

    def plot_bus_seating(self, seating):
        '''
        plot avg based on temp dict

        TODO: background of bus
        '''
        t_dict = seating
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
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        plt.scatter(x=x_arr, y=y_arr, s=5)#, marker='_')
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        # plt.axis('off') # set axis to be blank
        # plt.show()


        plt.savefig('results/seating_plot.png', dpi=300)
        print('Seating Plot Complete')
        return


    # function to run model with user input
    def model_run(self):
        '''
        1 call bus_out_array
        2 start plotting hist
        3 window curve
        4 5-min transmission likelihood
        5 Averaged by Run and by Step
        6 Infections by run
        7 Scatter of distance vs infection
        8 Transmission Rates

        '''

        # 1bus_seating = self.generate_bus_seating()
        bus_out_array, conc_array, out_mat, chance_nonzero, avg_mat = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var, self.window_var) # replace default with selected

        self.chance_nonzero = chance_nonzero
        self.conc_array = conc_array

        # 2
        plt.figure(figsize=(5,4))#, dpi=300)
        plt.gcf().set_size_inches(5,4)

        output_filepath = "output/bus_simulation_" + str(self.students_var) + '_' + str(self.mask_var)+ '_' + str(self.number_simulations) + '_' + str(self.trip_length) + '_' + str(self.seat_var) + '_' + str(self.window_var) # str(i) for i in [self.inputs]

        # bus_out_array = this case
        w_bus_out_array, w_conc_array, w_out_mat, w_chance_nonzero, w_avg_mat = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var, self.window_var) # WORST CASE

        b_bus_out_array, b_conc_array, b_out_mat, b_chance_nonzero, b_avg_mat = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var, self.window_var) # BEST CASE


        # 3
        # send plots to /output

        # concentration
        # x_arr = []
        # y_arr = []
        # for i in bus_seating.items():
        #     x_arr.append(i[1][1])
        #     y_arr.append(i[1][0] * 1.5 + 1)
        #
        # # get average of conc_array; avg_mat???
        #
        # rot = mpl.transforms.Affine2D().rotate_deg(180)
        # fig = plt.figure()
        # ax1 = fig.add_subplot(1, 2, 1)
        # ax1.matshow(out_mat, cmap="OrRd", norm=mpl.colors.LogNorm())
        # plt.arrow(-2,24,0,-26, head_width=0.2, head_length=0.2, fc='k', ec='k')
        # plt.scatter(x=x_arr, y=y_arr, s=5)
        # plt.gcf().set_size_inches(2,2)
        # # plt.suptitle('Relative Airflow Heatmap', fontsize=7.5)
        # plt.annotate(xy=(-1, -1), text='front', fontsize=5)
        # plt.annotate(xy=(-1, 24), text='back', fontsize=5)
        # plt.axis('off')
        #
        #
        # ax2 = fig.add_subplot(1,2,2)
        # ax2.matshow(out_mat, cmap="OrRd")#, norm=mpl.colors.LogNorm())
        # plt.arrow(-2,24,0,-26, head_width=0.2, head_length=0.2, fc='k', ec='k')
        # plt.scatter(x=x_arr, y=y_arr, s=5)
        # plt.gcf().set_size_inches(2,2)
        # plt.suptitle('Relative Airflow Heatmap', fontsize=7.5)
        # plt.annotate(xy=(-1, -1), text='front', fontsize=5)
        # plt.annotate(xy=(-1, 24), text='back', fontsize=5)
        # # log scale vs regular scale + 'be not afraid'
        # plt.axis('off')
        # fig.text(.1, .01, 'Averaged relative concentration of viral particles\nLeft heatmap is Log Normalized for visibility', fontsize=4)
        # plt.savefig('results/relative_airflow.png', dpi=300)
        #
        # print('relative airflow complete!')

        # HISTOGRAMS
        # Hist 1 Seating
        # print('start seating')
        # fig1, ax1 = plt.subplots()
        # seat_types = ['full', 'window', 'zigzag']
        # for s in seat_types:
        #     bus_out_array, conc_array, out_mat, chance_nonzero, avg_mat = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, s, self.window_var) # SEATING
        #     pd.Series(bus_out_array[2]).plot.hist(bins=np.arange(0, 0.12, 0.001), alpha=.5, ax=ax1)
        #
        # plt.legend(['Full Occupancy Seating', 'Window Seats Only', 'Zigzag Seating'])
        # plt.xlabel('Mean likelihood of transmission at each step')
        # plt.ylabel('Number of students with this average risk of transmission')
        # seat_filepath = output_filepath + '_seating.png'
        # fig1.savefig(seat_filepath, dpi=300)
        # print('seating complete')
        # plt.close(fig1)

        # Hist 2 Windows
        fig2, ax2 = plt.subplots()
        window_types = [0, 6]
        win_out_df = pd.DataFrame(columns=window_types)
        for w in window_types:
            bus_out_array, conc_array, out_mat, chance_nonzero, avg_mat = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var, w) # WINDOW
            pd.Series(bus_out_array[2]).plot.hist(bins=np.arange(0, 0.056, 0.001), alpha=.5, ax=ax2)

        plt.legend([0, 6])
        plt.xlabel('Mean likelihood of transmission at each step')
        plt.ylabel('Number of students with this average risk of transmission')
        seat_filepath_2 = output_filepath + '_windows.png'
        fig2.savefig(seat_filepath_2, dpi=300)
        plt.close(fig2)
        print('windows complete')

        # Hist 3 Masks
        fig3 = plt.figure(3)
        mask_amount = [1, .9, .8, .7]
        print('start masks')
        for m in mask_amount:
            bus_out_array, conc_array, out_mat, chance_nonzero, avg_mat = bus_sim(int(self.students_var), m, self.number_simulations, self.trip_length, self.seat_var, self.window_var) # SEATING
            pd.Series(bus_out_array[2]).plot.hist(bins=np.arange(0, 0.056, 0.001), alpha=.5)

        plt.legend(['100% Mask compliance', '90% Mask compliance', '80% Mask compliance', '70% Mask compliance'])
        plt.xlabel('Mean likelihood of transmission at each step')
        plt.ylabel('Number of students with this average risk of transmission')
        seat_filepath_3 = output_filepath + '_masks.png'
        fig3.savefig(seat_filepath_3, dpi=300)
        plt.close(fig3)
        print('masks complete')

        # # KDEPLOT and SCATTERPLOT
        # # KDE
        # pd.Series(bus_out_array).plot.kde(lw=2, c='r') # THIS KDEPLOT IS TO LOOK COOL AND DO NOTHING
        # rework bus_out_array into array of outputs:
        # All Transmission rates
        # Averaged Student/Run rates
        # Averaged /Step Student/Run rates
        # All Averaged /Step rates
        # print(len(bus_out_array))
        #     fig, axes = plt.figure()
        #     print('please')
        #
        #
        # fig, axs = plt.subplots(2,2)
        # fig.tight_layout()
        # # axs[0,0] = pd.Series(bus_out_array[0]).plot.kde(lw=2, color='blue')
        # # axs[1,0] = pd.Series(bus_out_array[1]).plot.kde(lw=2, color='r')
        # axs[0,0].hist(bus_out_array[0], bins=np.arange(0, .03, .001))
        # axs[0,0].set_title('All 5-minute transmission likelihoods')
        #
        # pd.Series(bus_out_array[1]).plot.kde(ax=axs[1,0])#), bins=14)#, bins=np.arange(0, .03, .003))
        # axs[1,0].set_title('Averaged by Run and by Step')
        #
        # axs[0,1].hist(pd.Series(bus_out_array[2]))#, bins=np.arange(0, .1, .001))
        # axs[0,1].set_title('Infections by run')
        #
        # # print(bus_out_array[3]["0"])
        # # axs[1,1] = fig.add_subplot(111)
        # axs[1,1].scatter(bus_out_array[5]["distance"], bus_out_array[5]["transmission rate"], s=2, color='green', label='far')
        # axs[1,1].scatter(bus_out_array[2]["distance"], bus_out_array[2]["transmission rate"], s=2, color='yellow', label='nearby')
        # axs[1,1].scatter(bus_out_array[3]["distance"], bus_out_array[3]["transmission rate"], s=2, color='red', label='neighbors')
        # axs[1,1].set_title('Distance from infected vs transmission rate')
        # axs[1,1].set_xlabel('Distance in Meters')
        # axs[1,1].set_ylabel('Transmission Rate')
        # plt.legend()
        # plt.savefig('results/transmission_rates.png', dpi=300)
        # plt.close(fig)


        # KDE2? One for each student with overlapped sections darker

        # SCATTER
            # Distance from initially infectious vs infection rate / 10000
        #



        return
