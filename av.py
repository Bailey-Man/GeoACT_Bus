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
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        plt.scatter(x=x_arr, y=y_arr, s=5)#, marker='_')
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
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
        bus_trip, conc_array, out_mat, chance_nonzero, avg_mat = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var, self.window_var) # replace default with selected

        x_arr = []
        y_arr = []
        for i in bus_seating.items():
            x_arr.append(i[1][1])
            y_arr.append(i[1][0] * 1.5 + 1)

        # get average of conc_array; avg_mat???

        rot = mpl.transforms.Affine2D().rotate_deg(180)
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.matshow(out_mat, cmap="OrRd", norm=mpl.colors.LogNorm())
        plt.arrow(-2,24,0,-26, head_width=0.2, head_length=0.2, fc='k', ec='k')
        plt.scatter(x=x_arr, y=y_arr, s=5)
        plt.gcf().set_size_inches(2,2)
        # plt.suptitle('Relative Airflow Heatmap', fontsize=7.5)
        plt.annotate(xy=(-1, -1), text='front', fontsize=5)
        plt.annotate(xy=(-1, 24), text='back', fontsize=5)
        plt.axis('off')


        ax2 = fig.add_subplot(1,2,2)
        ax2.matshow(out_mat, cmap="OrRd")#, norm=mpl.colors.LogNorm())
        plt.arrow(-2,24,0,-26, head_width=0.2, head_length=0.2, fc='k', ec='k')
        plt.scatter(x=x_arr, y=y_arr, s=5)
        plt.gcf().set_size_inches(2,2)
        plt.suptitle('Relative Airflow Heatmap', fontsize=7.5)
        plt.annotate(xy=(-1, -1), text='front', fontsize=5)
        plt.annotate(xy=(-1, 24), text='back', fontsize=5)
        # log scale vs regular scale + 'be not afraid'
        plt.axis('off')
        fig.text(.1, .01, 'Averaged relative concentration of viral particles\nLeft heatmap is Log Normalized for visibility', fontsize=4)
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
        bus_trip, conc_array, out_mat, chance_nonzero, avg_mat = bus_sim(int(self.students_var), self.mask_var, self.number_simulations, self.trip_length, self.seat_var, self.window_var) # replace default with selected
        self.chance_nonzero = chance_nonzero
        # print(chance_nonzero, 'more than none?')
        self.conc_array = conc_array
        # self.bus_trips.append(bus_trip)
        # print('model_run start')
        plt.figure(figsize=(5,4))#, dpi=300)
        plt.gcf().set_size_inches(5,4)

        # pd.Series(bus_trip).plot.kde(lw=2, c='r') # THIS KDEPLOT IS TO LOOK COOL AND DO NOTHING
        # rework bus_trip into array of outputs:
        # All Transmission rates
        # Averaged Student/Run rates
        # Averaged /Step Student/Run rates
        # All Averaged /Step rates
        # print(len(bus_trip))


        pd.Series(bus_trip[2]).plot.hist(color='blue', linewidth=2, edgecolor='black',bins=14, alpha=.7)
        # print('transmissions', len(bus_trip), bus_trip)
        if int(self.window_var) == 0:
            win_v = 'closed'
        else:
            win_v = 'open'
        plt.title(f'Average chance of infection with {win_v} windows')
        plt.ticklabel_format(axis="x")#, style="sci", scilimits=(0,0))

        plt.gca().set_xticklabels(['{:.1f}%'.format(x*100) for x in plt.gca().get_xticks()])
        # rescale y axis to be % based
        plt.xlabel('Chance of infection')
        plt.ylabel('Number of Students')
        plt.tight_layout()
        plt.savefig('results/window_curve.png', dpi=300)
        # plt.show()
        plt.close()

        # fig, axes = plt.figure()
        # print('please')
        fig, axs = plt.subplots(2,2)
        fig.tight_layout()
        # axs[0,0] = pd.Series(bus_trip[0]).plot.kde(lw=2, color='blue')
        # axs[1,0] = pd.Series(bus_trip[1]).plot.kde(lw=2, color='r')
        axs[0,0].hist(bus_trip[0], bins=np.arange(0, .03, .001))
        axs[0,0].set_title('All 5-minute transmission likelihoods')

        pd.Series(bus_trip[1]).plot.kde(ax=axs[1,0])#), bins=14)#, bins=np.arange(0, .03, .003))
        axs[1,0].set_title('Averaged by Run and by Step')

        axs[0,1].hist(pd.Series(bus_trip[2]))#, bins=np.arange(0, .1, .001))
        axs[0,1].set_title('Infections by run')

        # print(bus_trip[3]["0"])
        # axs[1,1] = fig.add_subplot(111)
        axs[1,1].scatter(bus_trip[5]["distance"], bus_trip[5]["transmission rate"], s=2, color='green', label='far')
        axs[1,1].scatter(bus_trip[4]["distance"], bus_trip[4]["transmission rate"], s=2, color='yellow', label='nearby')
        axs[1,1].scatter(bus_trip[3]["distance"], bus_trip[3]["transmission rate"], s=2, color='red', label='neighbors')
        axs[1,1].set_title('Distance from infected vs transmission rate')
        axs[1,1].set_xlabel('Distance in Meters')
        axs[1,1].set_ylabel('Transmission Rate')
        plt.legend()
        plt.savefig('results/transmission_rates.png', dpi=300)
        plt.close()


        temp_dict = self.generate_bus_seating()
        x_arr = []
        y_arr = []
        for i in temp_dict.items():
            x_arr.append(i[1][1])
            y_arr.append(i[1][0] * 1.5 + 1)
        fig2, ax = plt.subplots()
        plt.matshow(avg_mat, cmap="OrRd", norm=mpl.colors.LogNorm())
        plt.scatter(x=x_arr, y=y_arr, s=500)
        plt.arrow(-2,24,0,-26, head_width=1, head_length=1, fc='k', ec='k', lw=2)
        plt.annotate(xy=(-1, -1), text='front', fontsize=50)
        plt.annotate(xy=(-1, 24), text='back', fontsize=50)
        plt.axis('off')
        plt.savefig('results/conc_clean.png', dpi=300, bbox_inches='tight')

        # print(len(bus_trip[0]))
        # print(len(bus_trip[1]))
        # print(len(bus_trip[2]["0"]))
        # print(len(bus_trip[3]))





        print('model_run complete!')

        return
    def compare_models(self):


        return
