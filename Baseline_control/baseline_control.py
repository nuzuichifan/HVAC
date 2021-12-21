
import numpy as np
import torch
import model
import xlwt
cap_small_chiller = 1760
cap_big_chiller = 2810
big_g2 = 0.313387
big_g3 = 0.463710
big_Pref = 504
small_g2 = 0.1950291
small_g3 = 0.7241581
small_Pref = 314
############################# Setup the problem #############################
env = model.model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
############################# Neural Net class #############################
class model_based_control:
    def __init__(self):
        self.CCbig = 2810
        self.CCsmall = 1760
        # self.action_ratio_array = np.load("action_ratio_array.npy")
    def train(self):
        #主要就是在接受到系统冷负荷的时候进行修改，跑一轮之后就可以了
        CLs = env.reset()[0]
        print("CLs",CLs)
        ratio = 0
        book = xlwt.Workbook()

        CLs_data_sheet          = book.add_sheet('CLs', cell_overwrite_ok=True)
        r_sheet                 = book.add_sheet('r', cell_overwrite_ok=True)
        P_big_challer_two_sheet = book.add_sheet('P_big_challer_two', cell_overwrite_ok=True)
        P_big_tower_two_sheet   = book.add_sheet('P_big_tower_two', cell_overwrite_ok=True)
        P_big_pump_two_sheet    = book.add_sheet('P_big_pump_two', cell_overwrite_ok=True)


        P_small_challer_sheet   = book.add_sheet('P_small_challer', cell_overwrite_ok=True)
        P_small_tower_sheet     = book.add_sheet('P_small_tower', cell_overwrite_ok=True)
        P_small_pump_sheet      = book.add_sheet('P_small_pump', cell_overwrite_ok=True)

        on_off_sheet            = book.add_sheet('on_off', cell_overwrite_ok=True)

        Tcwr_big_sheet = book.add_sheet('Tcwr_big', cell_overwrite_ok=True)
        Tcwr_small_sheet = book.add_sheet('Tcwr_small', cell_overwrite_ok=True)

        Tcws_big_sheet = book.add_sheet('Tcws_big', cell_overwrite_ok=True)
        Tcws_small_sheet = book.add_sheet('Tcws_small', cell_overwrite_ok=True)
        row = 0
        while True:
            print("第"+str(row)+"个数据")
            flag_store = False
            on_off = [1, 1, 1]
            ##这边得判断只是给模型传递负荷分配比和组件的开闭状态
            if CLs <= self.CCbig:
                if CLs <= self.CCsmall:
                    if CLs <= 0.4 * self.CCsmall:
                        on_off = [0, 0, 0]  #所有冷机都关闭
                    else:
                        on_off = [0, 0, 1]  #只开一个小冷机
                else:
                    on_off = [1, 0, 0]  #只开一个大冷机
            else:
                if CLs <= self.CCbig + self.CCsmall:
                    on_off = [1, 0, 1]  #开一个大冷机和一个小冷机
                    flag_store = True
                else:
                    if CLs <= 2 * self.CCbig:
                        on_off = [1, 1, 0]  #只开两个大冷机
                    else:
                        on_off = [1, 1, 1]  #所有冷机都开着
                        flag_store = True
            s_,r,done,P_big_challer_two,P_big_tower_two,P_big_pump_two,P_small_challer,P_small_tower,P_small_pump,Tcwr_big,Tcwr_small,Tcws_big,Tcws_small = env.step(on_off)

            #记录数据，每一天的数据都要记录
            CLs_data_sheet.write(row, 0, str(CLs))
            r_sheet.write(row, 0, str(r))
            P_big_challer_two_sheet.write(row, 0, str(P_big_challer_two))
            P_big_tower_two_sheet.write(row, 0, str(P_big_tower_two))
            P_big_pump_two_sheet.write(row, 0, str(P_big_pump_two))

            P_small_challer_sheet.write(row, 0, str(P_small_challer))
            P_small_tower_sheet.write(row, 0, str(P_small_tower))
            P_small_pump_sheet.write(row, 0, str(P_small_pump))

            Tcwr_big_sheet.write(row, 0, str(Tcwr_big))
            Tcwr_small_sheet.write(row, 0, str(Tcwr_small))

            Tcws_big_sheet.write(row, 0, str(Tcws_big))
            Tcws_small_sheet.write(row, 0, str(Tcws_small))

            on_off_sheet.write(row, 0, str(on_off[0]))
            on_off_sheet.write(row, 1, str(on_off[1]))
            on_off_sheet.write(row, 2, str(on_off[2]))
            row += 1
            book.save("baseline_control_data_update_5_max" + '.xls')
            # if flag_store:
            #     print("ratio",ratio)
            #     print("CLs",CLs)
            #     print("r",r)
            if done:
                break
            CLs = s_[0]
if __name__ == "__main__":
    model_based_control = model_based_control()
    model_based_control.train()

