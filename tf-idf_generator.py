import pandas, csv, operator,nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def update_stopwords(stopset):
    with open('stop_words_modified.txt','r',encoding='utf8') as file:
        curr = file.readlines()
    for line in curr:
        curr_list = line.split()
        stopset.update(set(curr_list))
    return  stopset

def read_file(filename):
    data = pandas.read_csv(filename)
    text = data.description.str.replace(r'[^a-z\s&;]', '').str.replace('&\S+;', '').str.replace('\s+', ' ').tolist()
    return text


def compute_TFIDF():

    descriptionList = read_file('state_aggr_descr.csv')

    # may not be needed
    temp_list1 =[]
    for i in range(0,51):
        temp_list1.append(descriptionList[i])

    # convert to lower case
    temp_list1 = [x.lower() for x in temp_list1]

    #lemmatize
    lemmatizer = WordNetLemmatizer()
    temp_list=[]
    for i in range(0,len(temp_list1)):
        curr = temp_list1[i]
        curr_list = curr.split(" ")
        new_list =""
        for i in range(0, len(curr_list)):
            curr_word = lemmatizer.lemmatize(curr_list[i])
            new_list += curr_word+" "
        temp_list.append(new_list)

    # stop words to be removed
    stopset = set(stopwords.words('english'))
    stopset.update(['&quot','w/','&amp','&apos','quot'])
    stopset = update_stopwords(stopset)

    # TF-IDF computation
    vectorizer = TfidfVectorizer(stop_words=stopset,use_idf=True)
    X = vectorizer.fit_transform(temp_list)

    feature_names = vectorizer.get_feature_names()
    dense = X.todense()

    all_phrase_score ={}

    for i in range(len(temp_list)):
        episode = dense[i].tolist()[0]
        phrase_scores=[pair for pair in zip(range(0,len(episode)),episode) if pair[1]>0]
        sorted_phrase_scores = sorted(phrase_scores,key = lambda t : t[1] * -1 )
        for phrase, score in [(feature_names[word_id],score) for (word_id, score) in sorted_phrase_scores]:
            all_phrase_score[phrase]=score

    print(all_phrase_score)
    all_phrase_sorted = dict(sorted(all_phrase_score.items(),key = operator.itemgetter(1),reverse= True))

    with open('sort_uni.csv', 'w',newline='')as one:
        writer = csv.writer(one)
        for key, value in all_phrase_sorted.items():
            writer.writerow([key, value])

compute_TFIDF()
