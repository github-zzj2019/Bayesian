import os

def fileWalker(path,k):
    fileArray = []
    for l in range(1,26):
        if l>=(k-1)*5+1 and l<=(k-1)*5+5:
            continue
        else:
            eachpath = str(path+'\\'+str(l)+'.txt')
            fileArray.append(eachpath)
    return fileArray

def test_fileWalker(path,k):
    fileArray = []
    for l in range((k-1)*5+1,(k-1)*5+6):
        eachpath = str(path+'\\'+str(l)+'.txt')
        fileArray.append(eachpath)
    return fileArray

def textParse(bigString):    #input is big string, #output is word list
    import re
    listOfTokens = re.split('\W', bigString)
    return [tok.lower() for tok in listOfTokens if len(tok) >= 2]

def email_parser(email_path):
    clean_word = textParse(open(email_path, encoding='utf-8').read())
    return clean_word

def get_word(email_file,k):
    word_list = []
    word_set = []
    email_paths = fileWalker(email_file,k) #遍历email_fil目录，得到所有文件的地址；email_paths：地址数组
    for email_path in email_paths:
        clean_word = email_parser(email_path)
        word_list.append(clean_word)#词的列表的列表
        word_set.extend(clean_word)#词的集合
    return word_list, set(word_set)

def count_word_prob(email_list, union_set): #词频向量
    word_prob = {}
    for word in union_set:
        counter = 0
        for email in email_list:
            if word in email:
                counter += 1
            else:
                continue
        prob = (counter+1)/len(email_list) #拉普拉斯平滑处理
        word_prob[word] = prob #word_prob[]
    return word_prob
##############################################################

def filter(ham_word_pro, spam_word_pro, test_file, k):
    test_paths = test_fileWalker(test_file,k)#拿到测试集
    T=0
    F=0 #T 预测为垃圾邮件的个数， F 预测为正常邮件的个数
    for test_path in test_paths:
        email_spam_prob = 0.0 #P(W|S)
        spam_prob = 0.5 #P(S)
        ham_prob = 0.5 #P(W)
        file_name = test_path.split('\\')[-1]
        prob_dict = {}
        words = set(email_parser(test_path))
        for word in words:
            Psw = 0.0
            if word not in spam_word_pro:
                Psw = 0.4
            else:
                Pws = spam_word_pro[word]
                Pwh = ham_word_pro[word]
                Psw = spam_prob*(Pws/(Pwh*ham_prob+Pws*spam_prob))
            prob_dict[word] = Psw
        numerator = 1
        denominator_h = 1
        L = sorted(prob_dict.items(), key=lambda e:e[1], reverse=True)
        L = L[:15]
        for l in L:
            numerator *= l[1]
            denominator_h *= (1-l[1])
        email_spam_prob = round(numerator/(numerator+denominator_h), 4)

        if email_spam_prob > 0.95:
            T+=1
        else:
            F+=1
    return T,F

def main():
    ham_file = r'.\email\ham'
    spam_file = r'.\email\spam'
    chazhun=0.0 #预测为垃圾邮件的有多少是真的垃圾邮件
    chaquan=0.0 #真正的垃圾邮件有多少被识别出来了
    for k in range(1,6): #25个垃圾邮件、正常邮件，每次选择(k-1)*5+1 --- (k-1)*5+5作为测试集，其他的作为训练集，进行5折交叉验证，求出查准率、查全率取平均值
        ham_list, ham_set = get_word(ham_file,k)
        spam_list, spam_set = get_word(spam_file,k)
        union_set = ham_set | spam_set#建立词向量
        ham_word_pro = count_word_prob(ham_list, union_set)
        spam_word_pro = count_word_prob(spam_list, union_set)
        TP,FN=filter(ham_word_pro, spam_word_pro, spam_file, k)
        FP,TN=filter(ham_word_pro, spam_word_pro, ham_file, k)
        chazhun+=TP/(TP+FP)
        chaquan+=TP/(TP+FN)
    print("查准率："+str(chazhun/5))
    print("\n")
    print("查全率："+str(chaquan/5))

if __name__ == '__main__':
    main()
