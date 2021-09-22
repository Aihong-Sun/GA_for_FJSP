import numpy as np
import random

class Encode:
    def __init__(self,Matrix,Pop_size,J,J_num,M_num):
        self.Matrix=Matrix      #工件各工序对应各机器加工时间矩阵
        self.GS_num=int(0.1*Pop_size)      #全局选择初始化
        self.LS_num=int(0.5*Pop_size)     #局部选择初始化
        self.RS_num=int(0.4*Pop_size)     #随机选择初始化
        self.J=J                #各工件对应的工序数
        self.J_num=J_num        #工件数
        self.M_num=M_num        #机器数
        self.CHS=[]
        self.Len_Chromo=0
        for i in J.values():
            self.Len_Chromo+=i

    #生成工序准备的部分
    def OS_List(self):
        OS_list=[]
        for k,v in self.J.items():
            OS_add=[k-1 for j in range(v)]
            OS_list.extend(OS_add)
        return OS_list

    #生成初始化矩阵
    def CHS_Matrix(self, C_num):  # C_num:所需列数
        return np.zeros([C_num, self.Len_Chromo], dtype=int)

    def Site(self,Job,Operation):
        O_num = 0
        for i in range(len(self.J)):
            if i == Job:
                return O_num + Operation
            else:
                O_num = O_num + self.J[i + 1]
        return O_num

    #全局选择初始化
    def Global_initial(self):
        MS=self.CHS_Matrix(self.GS_num)
        OS_list= self.OS_List()
        OS=self.CHS_Matrix(self.GS_num)
        for i in range(self.GS_num):
            Machine_time = np.zeros(self.M_num, dtype=float)  # 机器时间初始化
            random.shuffle(OS_list)  # 生成工序排序部分
            OS[i] = np.array(OS_list)
            GJ_list = [i_1 for i_1 in range(self.J_num)]
            random.shuffle(GJ_list)
            for g in GJ_list:  # 随机选择工件集的第一个工件,从工件集中剔除这个工件
                h = self.Matrix[g]  # 第一个工件含有的工序
                for j in range(len(h)):  # 从工件的第一个工序开始选择机器
                    D = h[j]
                    List_Machine_weizhi = []
                    for k in range(len(D)):  # 每道工序可使用的机器以及机器的加工时间
                        Useing_Machine = D[k]
                        if Useing_Machine != 9999:  # 确定可加工该工序的机器
                            List_Machine_weizhi.append(k)
                    Machine_Select = []
                    for Machine_add in List_Machine_weizhi:  # 将这道工序的可用机器时间和以前积累的机器时间相加
                        #  比较可用机器的时间加上以前累计的机器时间的时间值，并选出时间最小
                        Machine_Select.append(Machine_time[Machine_add] + D[
                            Machine_add])
                    Min_time = min(Machine_Select)
                    K = Machine_Select.index(Min_time)
                    I = List_Machine_weizhi[K]
                    Machine_time[I] += Min_time
                    site=self.Site(g,j)
                    MS[i][site] = K
        CHS1 = np.hstack((MS, OS))
        return CHS1


    #局部选择初始化
    def Local_initial(self):
        MS = self.CHS_Matrix(self.LS_num)
        OS_list = self.OS_List()
        OS = self.CHS_Matrix(self.LS_num)
        for i in range(self.LS_num):
            random.shuffle(OS_list)  # 生成工序排序部分
            OS_gongxu = OS_list
            OS[i] = np.array(OS_gongxu)
            GJ_list = [i_1 for i_1 in range(self.J_num)]
            for g in GJ_list:
                Machine_time = np.zeros(self.M_num)  # 机器时间初始化
                h =self.Matrix[g]   # 第一个工件及其对应工序的加工时间
                for j in range(len(h)):  # 从工件的第一个工序开始选择机器
                    D = h[j]
                    List_Machine_weizhi = []
                    for k in range(len(D)):  # 每道工序可使用的机器以及机器的加工时间
                        Useing_Machine = D[k]
                        if Useing_Machine == 9999:  # 确定可加工该工序的机器
                            continue
                        else:
                            List_Machine_weizhi.append(k)
                    Machine_Select = []
                    for Machine_add in List_Machine_weizhi:  # 将这道工序的可用机器时间和以前积累的机器时间相加
                        Machine_Select.append(Machine_time[Machine_add]+D[Machine_add])
                    Machine_Index_add = Machine_Select.index(min(Machine_Select))
                    site = self.Site(g, j)
                    MS[i][site] = MS[i][site] + Machine_Index_add
        CHS1 = np.hstack((MS, OS))
        return CHS1

    def Random_initial(self):
        MS = self.CHS_Matrix(self.RS_num)
        OS_list = self.OS_List()
        OS = self.CHS_Matrix(self.RS_num)
        for i in range(self.RS_num):
            random.shuffle(OS_list)  # 生成工序排序部分
            OS_gongxu = OS_list
            OS[i] = np.array(OS_gongxu)
            GJ_list = [i_1 for i_1 in range(self.J_num)]
            A = 0
            for gon in GJ_list:
                Machine_time = np.zeros(self.M_num)  # 机器时间初始化
                g = gon  # 随机选择工件集的第一个工件   #从工件集中剔除这个工件
                h = np.array(self.Matrix[g])  # 第一个工件及其对应工序的加工时间
                for j in range(len(h)):  # 从工件的第一个工序开始选择机器
                    D = np.array(h[j])
                    List_Machine_weizhi = []
                    Site=0
                    for k in range(len(D)):  # 每道工序可使用的机器以及机器的加工时间
                        if D[k] == 9999:  # 确定可加工该工序的机器
                            continue
                        else:
                            List_Machine_weizhi.append(Site)
                            Site+=1
                    Machine_Index_add = random.choice(List_Machine_weizhi)
                    MS[i][A] = MS[i][A] + Machine_Index_add
                    A += 1
        CHS1 = np.hstack((MS, OS))
        return CHS1
if __name__=='__main__':
    Matrix=[
    [[2,3,4,9999,9999,9999],[9999,3,9999,2,4,9999],[1,4,5,9999,9999,9999]],     #第一个工件及其对应的机器加工时间
    [[3,9999,5,9999,2,9999],[4,3,9999,9999,6,9999],[9999,9999,4,9999,7,11]],    #第二个工件及其对应的机器加工时间
    [[5,6,9999,9999,9999,9999],[9999,4,9999,3,5,9999],[9999,9999,13,9999,9,12]],#第3个，。。。。
    [[9,9999,7,9,9999,9999],[9999,6,9999,4,9999,5],[1,9999,3,9999,9999,3]],     #第4个，。。。。
]
    Pop_size=10
    J={1:3,2:3,3:3,4:3}
    J_num=4
    M_num=6
    e=Encode(Matrix,Pop_size,J,J_num,M_num)
    CHS1=e.Global_initial()
    print('CHS1----->>>')
    print(CHS1)
    CHS2 = e.Random_initial()
    print('CHS2----->>>')
    print(CHS2)
    CHS3 = e.Local_initial()
    print('CHS3----->>>')
    print(list(CHS3))