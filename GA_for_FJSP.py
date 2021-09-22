import numpy as np
import random
from Decode_for_FJSP import Decode
from Encode_for_FJSP import Encode
import itertools
import matplotlib.pyplot as plt

class GA:
    def __init__(self):
        self.Pop_size=200       #种群数量
        self.P_c=0.8            #交叉概率
        self.P_m=0.3            #变异概率
        self.P_v=0.5            #选择何种方式进行交叉
        self.P_w=0.99            #采用何种方式进行变异
        self.Max_Itertions=100  #最大迭代次数

    #适应度
    def fitness(self,CHS,J,Processing_time,M_num,Len):
        Fit1=[]
        for i in range(len(CHS)):
            d = Decode(J, Processing_time, M_num)
            Fit1.append(d.Decode_1(CHS[i],Len))
        Fit2 = []
        for i in range(len(CHS)):
            d = Decode(J, Processing_time, M_num)
            Fit2.append(d.Decode_2(CHS[i], Len))

        return Fit1,Fit2

    #机器部分交叉
    def Crossover_Machine(self,CHS1,CHS2,T0):
        T_r=[j for j in range(T0)]
        r = random.randint(1, 10)  # 在区间[1,T0]内产生一个整数r
        random.shuffle(T_r)
        R = T_r[0:r]  # 按照随机数r产生r个互不相等的整数
        # 将父代的染色体复制到子代中去，保持他们的顺序和位置
        OS_1=CHS1[T0:2*T0]
        OS_2 = CHS2[T0:2 * T0]
        C_1 = CHS2[0:T0]
        C_2 = CHS1[0:T0]
        for i in R:
            K,K_2 = C_1[i],C_2[i]
            C_1[i],C_2[i] = K_2,K
        CHS1=np.hstack((C_1,OS_1))
        CHS2 = np.hstack((C_2, OS_2))
        return CHS1,CHS2

    #工序交叉部分
    def Crossover_Operation(self,CHS1, CHS2, T0, J_num):
        OS_1 = CHS1[T0:2 * T0]
        OS_2 = CHS2[T0:2 * T0]
        MS_1 =CHS1[0:T0]
        MS_2 = CHS2[0:T0]
        Job_list = [i for i in range(J_num)]
        random.shuffle(Job_list)
        r = random.randint(1, J_num - 1)
        Set1 = Job_list[0:r]
        Set2 = Job_list[r:J_num]
        new_os = list(np.zeros(T0, dtype=int))
        for k, v in enumerate(OS_1):
            if v in Set1:
                new_os[k] = v + 1
        for i in OS_2:
            if i not in Set1:
                Site = new_os.index(0)
                new_os[Site] = i + 1
        new_os = np.array([j - 1 for j in new_os])
        CHS1=np.hstack((MS_1,new_os))
        CHS2 = np.hstack((MS_2, new_os))
        return CHS1,CHS2

    def reduction(self,num,J,T0):
        T0=[j for j in range(T0)]
        K=[]
        Site=0
        for k,v in J.items():
            K.append(T0[Site:Site+v])
            Site+=v
        for i in range(len(K)):
            if num in K[i]:
                Job=i
                O_num=K[i].index(num)
                break
        return Job,O_num

    #机器变异部分
    def Variation_Machine(self,CHS,O,T0,J):
        Tr=[i_num for i_num in range(T0)]
        MS=CHS[0:T0]
        OS=CHS[T0:2*T0]
        # 机器选择部分
        r = random.randint(1, T0 - 1)  # 在变异染色体中选择r个位置
        random.shuffle(Tr)
        T_r = Tr[0:r]
        for i in T_r:
            Job=self.reduction(i,J,T0)
            O_i=Job[0]
            O_j =Job[1]
            Machine_using = O[O_i][O_j]
            Machine_time = []
            for j in Machine_using:
                if j != 9999:
                    Machine_time.append(j)
            Min_index = Machine_time.index(min(Machine_time))
            MS[i] = Min_index
        CHS=np.hstack((MS,OS))
        return CHS
    #工序变异部分
    def Variation_Operation(self, CHS,T0,J_num,J,Processing_time,M_num):
        MS=CHS[0:T0]
        OS=list(CHS[T0:2*T0])
        r=random.randint(1,J_num-1)
        Tr=[i for i in range(J_num)]
        random.shuffle(Tr)
        Tr=Tr[0:r]
        J_os=dict(enumerate(OS))    #随机选择r个不同的基因
        J_os = sorted(J_os.items(), key=lambda d: d[1])
        Site=[]
        for i in range(r):
            Site.append(OS.index(Tr[i]))
        A=list(itertools.permutations(Tr, r))
        A_CHS=[]
        for i in range(len(A)):
            for j in range(len(A[i])):
                OS[Site[j]]=A[i][j]
            C_I=np.hstack((MS,OS))
            A_CHS.append(C_I)
        Fit = []
        for i in range(len(A_CHS)):
            d = Decode(J, Processing_time, M_num)
            Fit.append(d.Decode_1(CHS, T0))
        return A_CHS[Fit.index(min(Fit))]

    def Select(self,Fit_value):
        Fit=[]
        for i in range(len(Fit_value)):
            fit=1/Fit_value[i]
            Fit.append(fit)
        Fit=np.array(Fit)
        idx = np.random.choice(np.arange(len(Fit_value)), size=len(Fit_value), replace=True,
                               p=(Fit) / (Fit.sum()))
        return idx

    def main(self,Processing_time,J,M_num,J_num,O_num):
        e = Encode(Processing_time, self.Pop_size, J, J_num, M_num)
        OS_List=e.OS_List()
        Len_Chromo=e.Len_Chromo
        CHS1=e.Global_initial()
        CHS2 = e.Random_initial()
        CHS3 = e.Local_initial()
        C=np.vstack((CHS1,CHS2,CHS3))
        Optimal_fit=9999
        Optimal_CHS=0
        x = np.linspace(0, 30, 30)
        x1=[x1 for x1 in range(self.Pop_size)]
        Best_fit=[]
        for i in range(self.Max_Itertions):
            Fit = self.fitness(C, J, Processing_time, M_num, Len_Chromo)
            plt.plot(x1,Fit[0],'-k')
            plt.plot(x1, Fit[1], linestyle='-.',c="black")
            plt.title('Comparision between two scheduling strategies')
            plt.ylabel('Cmax')
            plt.xlabel('Individual')
            plt.show()



            Best = C[Fit.index(min(Fit))]
            best_fitness = min(Fit)
            if best_fitness < Optimal_fit:
                Optimal_fit = best_fitness
                Optimal_CHS = Best
                Best_fit.append(Optimal_fit)
                print('best_fitness', best_fitness)
                d = Decode(J, Processing_time, M_num)
                Fit.append(d.Decode_1(Optimal_CHS, Len_Chromo))
                d.Gantt(d.Machines)
            else:
                Best_fit.append(Optimal_fit)
            Select = self.Select(Fit)
            print(len(Select))
            C=[C[Select_i-1] for Select_i in Select]
            for j in range(len(C)):
                offspring = []
                if random.random()<self.P_c:
                    N_i = random.choice(np.arange(len(C)))
                    if random.random()<self.P_v:
                        Crossover=self.Crossover_Machine(C[j],C[N_i],Len_Chromo)
                        # print('Cov1----->>>>>',len(Crossover[0]),len(Crossover[1]))
                    else:
                        Crossover=self.Crossover_Operation(C[j],C[N_i],Len_Chromo,J_num)
                    offspring.append(Crossover[0])
                    offspring.append(Crossover[1])
                if random.random()<self.P_m:
                    if random.random()<self.P_w:
                        Mutation=self.Variation_Machine(C[j],Processing_time,Len_Chromo,J)
                    else:
                        Mutation=self.Variation_Operation(C[j],Len_Chromo,J_num,J,Processing_time,M_num)
                    offspring.append(Mutation)
                if offspring !=[]:
                    # Fit = []
                    # for i in range(len(offspring)):
                    #     d = Decode(J, Processing_time, M_num)
                    #     Fit.append(d.Decode_1(offspring[i], Len_Chromo))
                    C[j] = random.choice(offspring)
        plt.plot(x, Best_fit,'-k')
        plt.title(
            'the maximum completion time of each iteration for flexible job shop scheduling problem')
        plt.ylabel('Cmax')
        plt.xlabel('Test Num')
        plt.show()

if __name__=='__main__':
    from MK01 import Processing_time, J, M_num, J_num, O_num
    g=GA()
    g.main(Processing_time,J,M_num,J_num,O_num)








