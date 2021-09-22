import matplotlib.pyplot as plt
from Jobs import Job
from Machines import Machine_Time_window
import numpy as np

class Decode:
    def __init__(self,J,Processing_time,M_num):
        self.Processing_time = Processing_time
        self.Scheduled = []  # 已经排产过的工序
        self.M_num = M_num
        self.Machines = []  # 存储机器类
        self.fitness = 0
        self.J=J            #
        for j in range(M_num):
            self.Machines.append(Machine_Time_window(j))
        self.Machine_State = np.zeros(M_num, dtype=int)  # 在机器上加工的工件是哪个
        self.Jobs = []     #存储工件类
        for k, v in J.items():
            self.Jobs.append(Job(k, v))
    #时间顺序矩阵和机器顺序矩阵
    def Order_Matrix(self,MS):
        JM=[]
        T=[]
        Ms_decompose=[]
        Site=0
        for S_i in self.J.values():
            Ms_decompose.append(MS[Site:Site+S_i])
            Site+=S_i
        for i in range(len(Ms_decompose)):
            JM_i=[]
            T_i=[]
            for j in range(len(Ms_decompose[i])):
                O_j=self.Processing_time[i][j]
                M_ij=[]
                T_ij=[]
                for Mac_num in range(len(O_j)):  # 寻找MS对应部分的机器时间和机器顺序
                    if O_j[Mac_num] != 9999:
                        M_ij.append(Mac_num)
                        T_ij.append(O_j[Mac_num])
                    else:
                        continue
                JM_i.append(M_ij[Ms_decompose[i][j]])
                T_i.append(T_ij[Ms_decompose[i][j]])
            JM.append(JM_i)
            T.append(T_i)
        return JM,T

    def Earliest_Start(self,Job,O_num,Machine):
        P_t=self.Processing_time[Job][O_num][Machine]
        last_O_end = self.Jobs[Job].Last_Processing_end_time  # 上道工序结束时间
        Selected_Machine=Machine
        M_window = self.Machines[Selected_Machine].Empty_time_window()
        M_Tstart = M_window[0]
        M_Tend = M_window[1]
        M_Tlen = M_window[2]
        Machine_end_time = self.Machines[Selected_Machine].End_time
        ealiest_start = max(last_O_end, Machine_end_time)
        if M_Tlen is not None:  # 此处为全插入时窗
            for le_i in range(len(M_Tlen)):
                if M_Tlen[le_i] >= P_t:
                    if M_Tstart[le_i] >= last_O_end:
                        ealiest_start=M_Tstart[le_i]
                        break
                    if M_Tstart[le_i] < last_O_end and M_Tend[le_i] - last_O_end >= P_t:
                        ealiest_start = last_O_end
                        break
        M_Ealiest = ealiest_start
        End_work_time = M_Ealiest + P_t
        return M_Ealiest, Selected_Machine, P_t, O_num,last_O_end,End_work_time

    def Earliest_Start2(self,Job,O_num,Machine):
        P_t=self.Processing_time[Job][O_num][Machine]
        last_O_end = self.Jobs[Job].Last_Processing_end_time  # 上道工序结束时间
        Selected_Machine=Machine
        M_window = self.Machines[Selected_Machine].Empty_time_window()
        M_Tstart = M_window[0]
        M_Tend = M_window[1]
        M_Tlen = M_window[2]
        Machine_end_time = self.Machines[Selected_Machine].End_time
        ealiest_start = max(last_O_end, Machine_end_time)
        if M_Tlen is not None:  # 此处为全插入时窗
            for le_i in range(len(M_Tlen)):
                if M_Tlen[le_i] >= P_t:
                    if M_Tstart[le_i] >= last_O_end:
                        ealiest_start=M_Tstart[le_i]
                        break
                    if M_Tstart[le_i] < last_O_end and M_Tend[le_i] - last_O_end >= P_t:
                        if M_Tlen[le_i]-P_t>7 and O_num<7:
                            ealiest_start=M_Tend[le_i]-P_t
                        else:
                            ealiest_start = last_O_end
                        break
        M_Ealiest = ealiest_start
        End_work_time = M_Ealiest + P_t
        return M_Ealiest, Selected_Machine, P_t, O_num,last_O_end,End_work_time

    #解码
    def Decode_1(self,CHS,Len_Chromo):
        MS=list(CHS[0:Len_Chromo])
        OS=list(CHS[Len_Chromo:2*Len_Chromo])
        Needed_Matrix=self.Order_Matrix(MS)
        JM=Needed_Matrix[0]
        for i in OS:
            Job=i
            O_num=self.Jobs[Job].Current_Processed()
            Machine=JM[Job][O_num]
            Para=self.Earliest_Start(Job,O_num,Machine)
            self.Jobs[Job]._Input(Para[0],Para[5],Para[1])
            if Para[5]>self.fitness:
                self.fitness=Para[5]
            self.Machines[Machine]._Input(Job,Para[0],Para[2],Para[3])
        return self.fitness

    # 解码
    def Decode_2(self, CHS, Len_Chromo):
        MS = list(CHS[0:Len_Chromo])
        OS = list(CHS[Len_Chromo:2 * Len_Chromo])
        Needed_Matrix = self.Order_Matrix(MS)
        JM = Needed_Matrix[0]
        for i in OS:
            Job = i
            O_num = self.Jobs[Job].Current_Processed()
            Machine = JM[Job][O_num]
            Para = self.Earliest_Start2(Job, O_num, Machine)
            self.Jobs[Job]._Input(Para[0], Para[5], Para[1])
            if Para[5] > self.fitness:
                self.fitness = Para[5]
            self.Machines[Machine]._Input(Job, Para[0], Para[2], Para[3])
        return self.fitness

    def Gantt(self,Machines):
        M = ['red', 'blue', 'yellow', 'orange', 'green', 'palegoldenrod', 'purple', 'pink', 'Thistle', 'Magenta',
             'SlateBlue', 'RoyalBlue', 'Cyan', 'Aqua', 'floralwhite', 'ghostwhite', 'goldenrod', 'mediumslateblue',
             'navajowhite',
             'navy', 'sandybrown', 'moccasin']
        for i in range(len(Machines)):
            Machine=Machines[i]
            Start_time=Machine.O_start
            End_time=Machine.O_end
            for i_1 in range(len(End_time)):
                # plt.barh(i,width=End_time[i_1]-Start_time[i_1],height=0.8,left=Start_time[i_1],\
                #          color=M[Machine.assigned_task[i_1][0]],edgecolor='black')
                # plt.text(x=Start_time[i_1]+0.1,y=i,s=Machine.assigned_task[i_1])
                plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.8, left=Start_time[i_1], \
                         color='white', edgecolor='black')
                plt.text(x=Start_time[i_1] + (End_time[i_1] - Start_time[i_1])/2-0.5, y=i, s=Machine.assigned_task[i_1][0])
        plt.yticks(np.arange(i + 1), np.arange(1, i + 2))
        plt.title('Scheduling Gantt chart')
        plt.ylabel('Machines')
        plt.xlabel('Time(s)')
        plt.show()

if __name__=='__main__':
    from Encode_for_FJSP import Encode
    Matrix = [[[5, 3, 5, 3, 3, 9999, 10, 9],
                  [10, 9999, 5, 8, 3, 9, 9, 6],
                  [9999, 10, 9999, 5, 6, 2, 4, 5]],

                 [[5, 7, 3, 9, 8, 9999, 9, 9999],
                  [9999, 8, 5, 2, 6, 7, 10, 9],
                  [9999, 10, 9999, 5, 6, 4, 1, 7],
                  [10, 8, 9, 6, 4, 7, 9999, 9999]],

                 [[10, 9999, 9999, 7, 6, 5, 2, 4],
                  [9999, 10, 6, 4, 8, 9, 10, 9999],
                  [1, 4, 5, 6, 9999, 10, 9999, 7]],

                 [[3, 1, 6, 5, 9, 7, 8, 4],
                  [12, 11, 7, 8, 10, 5, 6, 9],
                  [4, 6, 2, 10, 3, 9, 5, 7]],

                 [[3, 6, 7, 8, 9, 9999, 10, 9999],
                  [10, 9999, 7, 4, 9, 8, 6, 9999],
                  [9999, 9, 8, 7, 4, 2, 7, 9999],
                  [11, 9, 9999, 6, 7, 5, 3, 6]],

                 [[6, 7, 1, 4, 6, 9, 9999, 10],
                  [11, 9999, 9, 9, 9, 7, 8, 4],
                  [10, 5, 9, 10, 11, 9999, 10, 9999]],

                 [[5, 4, 2, 6, 7, 9999, 10, 9999],
                  [9999, 9, 9999, 9, 11, 9, 10, 5],
                  [9999, 8, 9, 3, 8, 6, 9999, 10]],

                 [[2, 8, 5, 9, 9999, 4, 9999, 10],
                  [7, 4, 7, 8, 9, 9999, 10, 9999],
                  [9, 9, 9999, 8, 5, 6, 7, 1],
                  [9, 9999, 3, 7, 1, 5, 8, 9999]]]
    Pop_size = 10
    J = {1: 3, 2: 4, 3: 3, 4: 3, 5: 4, 6: 3, 7: 3, 8: 4}
    M_num = 8
    J_num = 8
    O_num = 27

    e = Encode(Matrix, Pop_size, J, J_num, M_num)
    L=e.Len_Chromo
    CHS1 = e.Global_initial()
    print('CHS1----->>>')
    print(CHS1)
    CHS2 = e.Random_initial()
    print('CHS2----->>>')
    print(CHS2)
    CHS3 = e.Local_initial()
    print('CHS3----->>>')
    print(CHS3)
    C=CHS1[0]
    d=Decode(J,Matrix,M_num)
    d.Decode(C,L)






