import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import markdown
import pdfkit
from datetime import datetime


def main():

    # dataframe = read_data()
    # splitted_df = split_date(dataframe)
    # sorted_df = splitted_df.sort_values(by='start_date')
    # exam_start_date=sorted_df.loc[0,'start_date']
    # print(exam_start_date)
    # score,conflicts_df = big_exams_early(splitted_df)
    # get_output(conflicts_df,1,'html');


# ------------------------ One Exam Per Day ------------------------------------

    """ 
   
    Comment Line for the illia

    Input:
    coursemat_df
    a file contains just one columns as 'courseNumber;matnr'
    # That means we have exams and student who is taking this exam.
                
                
    """
    # exam_plan = pd.read_excel("datafiles/FIW_Exams_2022ws.xlsx")
    # coursemat_df = pd.read_csv("datafiles/Pruefungsanmeldungen_anonmous.csv")

    # exam_plan = split_date(exam_plan)
    # coursemat_df = split_course_matnr(coursemat_df)
    # result = one_exam_per_day(exam_plan, coursemat_df)
    # get_output(result,1,'html');
    exam_plan, course_stud = create_df()
    
    room_capacity(exam_plan,course_stud)



def read_data():

    df=pd.read_excel("datafiles/FIW_Exams_2022ws.xlsx")
    return df
def create_df():
    exam_plan = pd.read_excel("datafiles/FIW_Exams_2022ws.xlsx")
    coursemat_df = pd.read_csv("datafiles/Pruefungsanmeldungen_anonmous.csv")

    # split into two columns
    coursemat_df[['courseNumber','matnr']] = coursemat_df['courseNumber;matnr'].str.split(';',expand=True)

    # del the first columns that is 'courseNumber;matnr'
    coursemat_df = coursemat_df.drop('courseNumber;matnr',axis=1)
    # first column is the course number and each row is the students who takes it
    course_stud = coursemat_df.groupby('courseNumber')['matnr'].apply(list)
    #turns into data frame(courseNumber,matnr) and adds a column shows the index for each row by using reset index method
    course_stud = course_stud.to_frame().reset_index()
 
    #courseNumber -> LV-Nr
    course_stud.columns = ['LV-Nr.', 'matnr']
    # this column's type turns into the string from object
    course_stud['LV-Nr.'] = course_stud['LV-Nr.'].astype(str)
    # this column's type turns into the string from object
    exam_plan['LV-Nr.'] = exam_plan['LV-Nr.'].astype(str)

    return exam_plan, course_stud  
#--------------------Processing functions--------------------#

def room_capacity(exam_plan,course_stud):
  
    
    #two table are merged via one common column.
    merged_df = pd.merge(exam_plan[['LV-Nr.', 'HS']], course_stud, on='LV-Nr.')

    merged_df['total_student'] = merged_df['matnr'].apply(lambda x: len(x))

    def calculate_total_capacity(row):


        import json

        # Read the json
        with open('./datafiles/capacity.json') as f:
            capacity = json.load(f)
        
        # Receive the strings in HS column and split them according to ,
        elements = row['HS'].split(', ')
    
        # reaching the room which you want to access
        rooms = capacity['Exam-room-capacities']
        room = None
    
        total = 0;
        for i in elements:
            for s in rooms.values():
                for r in s:
                    if r['Name'] == i:
                        room = r
                        # if you change this part you can also receive other capacities as well
                        total = total + room['Klausur-capacity 2']
                    
                
                if room:
                    break

        # Receiving total capacity
        return total

    # call the function for each row and add the result to a new column
    merged_df['Total Capacity'] = merged_df.apply(calculate_total_capacity, axis=1)

    x = merged_df['total_student'].values
    y = merged_df['Total Capacity'].values

    '''
    x = total student
    y = total capacity
    formula => d = |ax1 + by1 + c| / (a^2 + b^2)^0.5

    y = mx + b
    mx + b - y = 0
    m * total student - b + total capacity / (m^2 + 1)^0.5
    
    distance is 0 in terms of best case, we are finding max value via merged_df['distance'].max()

    dividing each distance value by the maximum distance turns the distances into ratios between 0 and 1 (merged_df['distance'] / merged_df['distance'].max()) Subtracting from 1 then transforms the scores into a score range where the highest score is 1 and the lowest score is 0. (1 - merged_df['distance'] / merged_df['distance'].max()) We did this because small distance should get the greater point
    '''
    m, b = np.polyfit(x, y, 1)

    # calculate the distance between line and dots. calculate the score
    merged_df['distance'] = abs(merged_df['total_student'] * m - merged_df['Total Capacity'] + b) / ((m**2 + 1)**0.5)
    merged_df['score'] = (1 - merged_df['distance'] / merged_df['distance'].max()) * 100

    total_score = merged_df['score'].sum()
    score_penalty = total_score / (len(merged_df) * merged_df['score'].max()) 

    print(score_penalty)
    print(merged_df)
    
    
    
    plt.scatter(x, y)

    # draw the line
    fit_fn = np.poly1d([m, b])
    plt.plot(x, fit_fn(x), '--k')

    # show the graph
    plt.show()

    # save the graph to the file
    plt.savefig('scatter_plot.png')


    

def split_date(dataframe):
     '''
     Input:
     dataframe: exam dataframe with type pandas.core.frame.DataFrame
   
     Output:
     pandas.core.frame.Dataframe with splitted date in two new columns:
                             'start_date', 'end_date' with dtype datetime64[ns]
   
     '''
     splitted_df = dataframe
     splitted_df[['start_date', 'end_date']] = dataframe['Datum, Uhrzeit (ggf. sep. Zeitplan beachten)'].str.split(" - ", expand = True)
     splitted_df[['start_date', 'end_date']] = pd.to_datetime(splitted_df[['start_date', 'end_date']].stack(), format='%Y-%m-%dT%H:%M').unstack()
    
     return splitted_df

def split_course_matnr(dataframe):
     '''
     Input:
     dataframe: dataframe with courseNumber and matnr with type pandas.core.frame.DataFrame
   
     Output:
     pandas.core.frame.Dataframe with splitted course number and matnr in two new columns:
                             'courseNumber', 'matnr' with dtype string
   
     '''
     splitted_df = dataframe
     splitted_df[['courseNumber', 'matnr']] = dataframe['courseNumber;matnr'].str.split(";", expand = True)    
     return splitted_df
    
def one_exam_per_day(exam_plan, coursemat_df):
    """
    Input:
    exam_plan: Exam dataframe with type pandas.core.frame.DataFrame. 
                It must be splitted with split_date function beforehand 
                
    coursemat_df: dataframe with type pandas.core.frame.Dataframe.
                It must be splitted with split_course_matnr function beforehand
                
    Output:
    conflicts dataframe, score and a plot of the graph
    """
    
    def f(x):
        return (1/2) ** (5*coursemat_df['matnr'].nunique()/1000)
    
    course_stud = coursemat_df.groupby('courseNumber')['matnr'].apply(list)
    course_stud = course_stud.to_frame().reset_index()
    course_stud.columns = ['LV-Nr.', 'matnr']
    course_stud['LV-Nr.'] = course_stud['LV-Nr.'].astype(str)
    exam_plan['LV-Nr.'] = exam_plan['LV-Nr.'].astype(str)
    merged_df = pd.merge(exam_plan, course_stud, on='LV-Nr.')
    merged_df['start_date'] = pd.to_datetime(merged_df['start_date'])
    merged_df['date'] = merged_df['start_date'].dt.date
    
    
    # Create a dictionary to store the conflicts
    conflicts = {}
    # Loop through each row of the dataframe
    for i, row in merged_df.iterrows():
        # Get the date and students for the current row
        date = row['date']
        students = row['matnr']
        # Check if any of the students have already been seen on the same date
        for student in students:
            if student in conflicts and date in conflicts[student]:
                # If the student is already in the conflicts dictionary for the current date,
                # add the current exam name to the list of conflicting exams for the student
                conflicts[student][date].append(row['Lehrveranstaltung'])
            elif student in conflicts:
                # If the student is already in the conflicts dictionary but not for the current date,
                # add the current date and exam name to the conflicts dictionary for the student
                conflicts[student][date] = [row['Lehrveranstaltung']]
            else:
                # If the student is not yet in the conflicts dictionary, add the student and
                # the current date and exam name to the conflicts dictionary
                conflicts[student] = {date: [row['Lehrveranstaltung']]}

    # Create a new dataframe to store the conflicts
    conflicts_df = pd.DataFrame(columns=['student_id', 'exam_names', 'date'])

    # Loop through each student in the conflicts dictionary
    for student, dates in conflicts.items():
        # Loop through each date for the student
        for date, exams in dates.items():
            # If the student has more than one exam on the date, add a row to the conflicts dataframe
            if len(exams) > 1:
                conflicts_df = conflicts_df._append({
                    'student_id': student,
                    'exam_names': exams,
                    'date': date
                }, ignore_index=True)
    conflicts_amount = conflicts_df['exam_names'].apply(lambda x: len(x)).sum() - len(conflicts_df)
    
    return conflicts_df
  
def big_exams_early(splitted_df):
    '''
    
    Input: 
    splitted_df: Exam dataframe with type pandas.core.frame.DataFrame. It must be splitted with split_date function beforehand
    
    Output: 
    Score with type float
    np.array object containing: 1. days difference; 2. student count; 3. exam name
    saves a plot with file name big_exams_early.png
    
    '''
    
    df = splitted_df
    
    sorted_date = df.sort_values(by='start_date')
    exam_start_date = sorted_date.loc[0,'start_date']
    
    df['delta'] = (df.start_date - exam_start_date).dt.days
    
    subjects_sorted = df.sort_values('Anzahl', ascending=False)
    latest_day = df['delta'].max()
    
    stud_counts = np.array(subjects_sorted.Anzahl)
    timeline = np.linspace(0, latest_day, num=len(stud_counts))
    
    ### Compute dots ###
    
    dots = {0: stud_counts[0]}
    for i in range(1, latest_day+1):
        diff = np.abs(timeline - i)
        sorted_indices = np.argsort(diff)

        index1 = sorted_indices[0]
        index2 = sorted_indices[1]
        
        t = (i - timeline[index1])/(timeline[index2]-timeline[index1])
        
        y = (1-t) * stud_counts[index1] + t * stud_counts[index2]
        
        dots[i] = y
        
    ### Compute score ###
    
    neg_score = 0
    arr = []
    for row in df.itertuples():
        if row.Anzahl > dots[row.delta]:
            neg_score = neg_score + np.abs(row.Anzahl - dots[row.delta])
            arr.append([row.delta, row.Anzahl, row.Lehrveranstaltung])
    arr = np.array(arr)
    worst_score = np.sum(df.Anzahl) - np.min(stud_counts)
    score = 1 - neg_score/worst_score
    
    ### Create plot ###
    
    plt.figure(figsize=(15, 10))
    plt.plot(timeline, stud_counts)
    
    dots_y = np.array(arr[:, 1], dtype=int)
    dots_x = np.array(arr[:, 0], dtype=int)
    subj_names = arr[:, 2]
    plt.scatter(dots_x, dots_y, s=10, color='red')
    
    for i in range(len(dots_x)):
        plt.text(dots_x[i], dots_y[i], subj_names[i], fontsize=6)
    plt.title('Big exams early conflicts')
    plt.xlabel('Day')
    plt.ylabel('Student count')
    plt.savefig('big_exams_early.png')
    
    ### Reformat conflict array to dataframe, return score and conflict dataframe ###
    
    conflicts_df = pd.DataFrame(arr, columns=['days_diff', 'stud_count', 'exam_name'])
    return score, conflicts_df
  
  #---------------------------------------------------#



  

  #---------------Output Processes-----------------------# 

def create_html(example_df):

    html= '''

    <html>
    <head>
    </head>
    <body>
      <main >
    <h1 style="text-align:center">Exam Quality Control</h1>

    <div style="margin: auto;width: 1200px;display: flex;gap:6rem;justify-content: center;">
        <div>
            <h2>Lists of Conflicts:</h2>

            <table style=" border: 1px solid;  border-collapse: collapse;">
               
        
          
    
    '''
    
   # Tablo başlıkları
    html += '<tr>'
    for col_name in example_df.columns:
        html += f'<th>{col_name}</th>'
    html += '</tr>'

    # Tablo verileri
    for i in range(len(example_df)):
        html += '<tr style="text-align:center;">'
        for j in range(len(example_df.columns)):
            cell_data = example_df.iloc[i, j]
            html += f'<td style="padding:1rem">{cell_data}</td>'
        html += '</tr>'


    html += '''
       
    </table>
    </ul>
 
    </div>
    <div style="margin-top: 4rem">
    <img src="./Thws-logo_English.png" style=" width: 400px" alt="big exams early">
    </div>
    </div>
    <img src="./big_exams_early.png"  alt="big exams early">
    </main>
    </body>
    </html>
    '''
    
    return html

def get_output(example_df,score,output_type):



    

    # create markdown text based on the coming data
    # in case that we need mark down again
    # markdown_text = f""" """

    # converts the markdown text into html
    # html = markdown.markdown(markdown_text)
    
    html = create_html(example_df);  


    if output_type == 'html':

        file_directory = "output.html"

        #creates a file
        file = open(file_directory,"w",encoding="utf-8")

        file.write(html)
        print('Printing Process is successfully ended')

        file.close()
    
    elif output_type == 'pdf':

          # in case that we need pdf again
   
        path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

        # html = markdown.markdown(markdown_text)
        path_to_file = 'output.html'

        #Point pdfkit configuration to wkhtmltopdf.exe
        # config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
        pdfkit.from_string(html, output_path='sample.pdf', configuration=config)


if __name__ == '__main__':
    main()
