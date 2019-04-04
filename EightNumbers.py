'''
Created on Mar 27, 2019

@author: neal
'''
import numpy as np
import sortedcontainers

class A_Star():
    def __init__(self,start,end):
        #star和end为3*3的list
        self.find_deep=[-1]*400000 #所有状态的深度，-1表示该状态未生成
        self.find_parent=[-1]*400000 #所有状态的parent
        self.factorial=[1,1,2,6,24,120,720,5040,40320] #0～8的阶乘
        self.search_count=0 #计算总搜索次数
        self.errorFlag=False
        self.start=start
        self.end=end
        self.open=sortedcontainers.SortedList([])
        #我们不需要close列表
        
    class Node():
        #这是储存在open里的单位，每个Node对应一个状态
        def __init__(self,idx,cost):
            self.idx=idx #该状态的康托展开
            self.cost=cost #该状态到目标状态的距离估计
        def __lt__(self,other):
            return self.cost>other.cost
           
    def Solution(self):
        #解法的主函数
        #首先检查输入是否合法，并把输入从3*3的list变为1*9的list
        self.start=self.check_input(self.start)
        self.end=self.check_input(self.end)       
        if self.errorFlag==True:
            print("Errors.")
            return
        #检查是否有解
        if not self.have_solution():
            print("No result.")
            return
        #初始化
        self.cantorstart=self.cantor(self.start)
        self.cantorend=self.cantor(self.end) 
        current=self.Node(self.cantorstart,self.get_hcost(self.start))
        self.find_deep[self.cantorstart]=0
        while True:
            #检查是否到达目标状态
            if current.idx==self.cantorend:
                print("The Answer is:")
                self.print_result(current)
                return 
            #否则，延展当前状态，并从open中提取cost最小的作为下一个状态
            self.extension(current)
            current=self.open.pop()
            self.search_count+=1
            
    def extension(self,parent):
        #延展子状态
        #寻找0在哪个位置
        state=self.un_cantor(parent.idx)
        for i in range(9):
            if state[i]==0:
                position=i
                break
        #检查上下左右是否能走，并生成相应的子状态
        #上
        if position//3!=0:
            temp=state*1
            temp[position]=temp[position-3]
            temp[position-3]=0
            self.update_open(temp,parent) 
        #下     
        if position//3!=2:
            temp=state*1
            temp[position]=temp[position+3]
            temp[position+3]=0
            self.update_open(temp,parent)
        #左
        if position%3!=0:
            temp=state*1
            temp[position]=temp[position-1]
            temp[position-1]=0
            self.update_open(temp,parent)
        #右
        if position%3!=2:
            temp=state*1
            temp[position]=temp[position+1]
            temp[position+1]=0 
            self.update_open(temp,parent)
            
    def print_result(self,current):
        #打印结果
        idx=current.idx
        result=[self.un_cantor(idx)]
        while self.find_parent[idx]!=-1:
            result.append(self.un_cantor(self.find_parent[idx]))
            idx=self.find_parent[idx]
        result.reverse()
        for i in range(len(result)):
            temp=np.matrix([result[i][0:3],result[i][3:6],result[i][6:9]])
            if i==0:
                print("\nthe original situation is:")
            else:
                print("\nthe %ith step is:" %i)
            print(temp) 
        print("\nThat is what we want. \nTotal number of steps is %d." %(len(result)-1))
        print("Total number of searches is %d." %self.search_count)
    
    def have_solution(self):
        #利用逆序数检查是否有解
        result=[0,0]
        for i in range(9):
            for j in range(i):
                if self.start[i]<self.start[j] and self.start[i]:
                    result[0]+=1
                if self.end[i]<self.end[j] and self.end[i]:
                    result[1]+=1
        return result[0]%2==result[1]%2
    
    def get_hcost(self,state):
        #计算从目前状态到目标状态的距离估计，即h(x)
        result=0
        for i in range(9):
            for j in range(9):
                if state[i]==self.end[j]:
                    result+=(abs(i//3-j//3)+abs(i%3-j%3))*(state[i])
                    #这里采用了每个数字回到目标位置的最小步数乘以数字作为权重的求和
                    #这是因为，我们希望计算机优先复原某几个数字，而不是均等对待
                    #实证表明这样比单纯求和效率高
        return result
    
    def update_open(self,temp,parent):
        #延展出子状态后，检查是否生成过，若未生成过，则加入open
        idx=self.cantor(temp)
        if self.find_deep[idx]==-1:
            self.find_deep[idx]=self.find_deep[parent.idx]+1
            self.find_parent[idx]=parent.idx
            self.open.add(self.Node(idx,self.find_deep[parent.idx]+1+self.get_hcost(temp)))
        #若生成过，但该处深度更小，则更新深度
        elif  self.find_deep[idx]>self.find_deep[parent.idx]+1:
            self.find_deep[idx]=self.find_deep[parent.idx]+1                
            self.find_parent[idx]=parent.idx
    
    def cantor(self,state):
        #康托展开
        result=0
        for i in range(9):
            count=0
            for j in range(i,9):
                if(state[i]>state[j]):
                    count+=1
            result+=count*self.factorial[9-i-1]        
        return result
    
    def un_cantor(self,idx):
        #逆康托展开
        number=[0,1,2,3,4,5,6,7,8]
        result=[0]*9
        for i in range(9):
            t=idx//self.factorial[9-i-1]
            idx%=self.factorial[9-i-1]
            result[i]=number[t]
            number.pop(t)
        return result
    
    def check_input(self,state):
        #检查输入是否合法，并将3*3转换为1*9
        #检查是否已有error，若有，则跳过本次检查
        if self.errorFlag==True:
            return
        result=[0]*9
        #检查输入形式是否正确
        try:
            for i in range(3):
                for j in range(3):
                    result[3*i+j]=state[i][j]
        except:
            print("The input is illegal.")
            self.errorFlag=True
            return
        #检查输入是否为0-8的排序
        if set(result)!={1,2,3,4,5,6,7,8,0}:
            print("The input is illegal.")
            self.errorFlag=True
        return result
    
#测试
start=[[1,0,4],[7,3,5],[8,6,2]]
end=[[1,3,2],[7,0,4],[6,5,8]]
A_Star(start,end).Solution()
