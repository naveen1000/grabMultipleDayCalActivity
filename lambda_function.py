import json
import mysql.connector
from io import StringIO, BytesIO
from datetime import datetime, timedelta,date 
from matplotlib import pyplot as plt
import numpy as np
import telegram
import os.path
import boto3

mydb = mysql.connector.connect(
  host="database-1.cyxb0drmxfft.us-east-1.rds.amazonaws.com",
  user="admin",
  password="admin123",

  database="CalDB"
)
mycursor = mydb.cursor()
s3 = boto3.client('s3')
bot = telegram.Bot('758389493:AAExlM5jAb1OvyG9ZBYXyPzbnaO2SslQUWo')

def weekly_bar_chart(p_from_date,p_to_date):
  sql = """with cte as 
    (select selected_date from 
    (select adddate('1970-01-01',t4*10000 + t3*1000 + t2*100 + t1*10 + t0) selected_date from
    (select 0 t0 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t0,
    (select 0 t1 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t1,
    (select 0 t2 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t2,
    (select 0 t3 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t3,
    (select 0 t4 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t4) v
    where selected_date between '""" + str(p_from_date) + "' and '" + str(p_to_date) + """')
    select c.selected_date, 'Naveen Routine' Calendar, coalesce(sum(TIME_TO_SEC(t.event_diff_time))/3600,0) Time_Spent
    from cte c left join CalDB.cal_events_data t
    on c.selected_date = t.event_start_date
    and t.event_cal_name = 'Naveen Routine' 
    group by c.selected_date,t.event_cal_name
    UNION
    select c.selected_date,'Naveen Daily Routine' Calendar, coalesce(sum(TIME_TO_SEC(t.event_diff_time))/3600,0) Time_Spent
    from cte c left join CalDB.cal_events_data t
    on c.selected_date = t.event_start_date
    and t.event_cal_name = 'Naveen Daily Routine' 
    group by c.selected_date,t.event_cal_name
    UNION
    select c.selected_date,'Naveen Work Calendar' Calendar, coalesce(sum(TIME_TO_SEC(t.event_diff_time))/3600,0) Time_Spent
    from cte c left join CalDB.cal_events_data t
    on c.selected_date = t.event_start_date
    and t.event_cal_name = 'Naveen Work Calendar' 
    group by c.selected_date,t.event_cal_name
    UNION
    select c.selected_date,'Naveen Personal Work' Calendar, coalesce(sum(TIME_TO_SEC(t.event_diff_time))/3600,0)  Time_Spent
    from cte c left join CalDB.cal_events_data t
    on c.selected_date = t.event_start_date
    and t.event_cal_name = 'Naveen Personal Work' 
    group by c.selected_date,t.event_cal_name
    UNION
    select c.selected_date,'Naveen Mobile TV Usage' Calendar, coalesce(sum(TIME_TO_SEC(t.event_diff_time))/3600,0)  Time_Spent
    from cte c left join CalDB.cal_events_data t
    on c.selected_date = t.event_start_date
    and t.event_cal_name = 'Naveen Mobile TV Usage' 
    group by c.selected_date,t.event_cal_name
    UNION
    select c.selected_date,'Naveen Sleep Calendar' Calendar, coalesce(sum(TIME_TO_SEC(t.event_diff_time))/3600,0)  Time_Spent
    from cte c left join CalDB.cal_events_data t
    on c.selected_date = t.event_start_date
    and t.event_cal_name = 'Naveen Sleep Calendar' 
    group by c.selected_date,t.event_cal_name
    order by Calendar,selected_date"""
  mycursor.execute("SET SESSION time_zone = '+5:30';")
  mycursor.execute(sql)
  myresult = mycursor.fetchall()

  routine_x_indexes = []
  routine_y_indexes = []
  daily_routine_y_indexes = []
  work_y_indexes = []
  personal_work_y_indexes = []
  sleep_y_indexes = []
  mobile_y_indexes = []
 
  for x in myresult:    
    print(x[0], ' ' ,x[1], ' ' , float(x[2]) ) 
    if x[1] == 'Naveen Routine':
        routine_y_indexes.append(float(x[2]))
        routine_x_indexes.append(str(x[0]))
    elif x[1] == 'Naveen Daily Routine':
        daily_routine_y_indexes.append(float(x[2]))
    elif x[1] == 'Naveen Work Calendar':
        work_y_indexes.append(float(x[2]))
    elif x[1] == 'Naveen Personal Work':
        personal_work_y_indexes.append(float(x[2]))    
    elif x[1] == 'Naveen Sleep Calendar':
        sleep_y_indexes.append(float(x[2]))
    elif x[1] == 'Naveen Mobile TV Usage':
        mobile_y_indexes.append(float(x[2]))  
        
  x_indexes = np.arange(len(routine_x_indexes))
  width = 0.5
  plt.cla()
  plt.clf()
  img_data = BytesIO()
  fig, ax = plt.subplots()
  NWC  = ax.bar(x_indexes - (width/1.5), work_y_indexes,width = width/4 ,color = "#7bd148" , label = "Naveen Work Calendar") 
  NPW = ax.bar(x_indexes - (width/2.5) , personal_work_y_indexes,width = width/4 ,color = "#42d692" , label = "Naveen Personal Work")
  NDR = ax.bar(x_indexes - (width/7.5), daily_routine_y_indexes,width = width/4 ,color = "#b99aff" , label = "Naveen Daily Routine")
  NR = ax.bar(x_indexes + (width/7.5), routine_y_indexes,width = width/4 ,color = "#9a9cff" , label = "Naveen Routine")
  NMU = ax.bar(x_indexes + (width/2.5), mobile_y_indexes,width = width/4 ,color = "#d06b64" , label = "Naveen Mobile TV Usage")
  NSC = ax.bar(x_indexes + (width/1.5), sleep_y_indexes,width = width/4 ,color = "#cabdbf" , label = "Naveen Sleep Calendar")
  ax.set_ylabel('Hours Spent')
  ax.set_title( p_from_date + ' to ' + p_to_date)  
  ax.set_xticks(ticks=x_indexes, labels= routine_x_indexes)
  #ax.legend()
  ax.bar_label(NWC, padding=3)
  ax.bar_label(NPW, padding=3) 
  ax.bar_label(NDR, padding=3)
  ax.bar_label(NR, padding=3)
  ax.bar_label(NMU, padding=3)
  ax.bar_label(NSC, padding=3)
  fig.tight_layout()
  #plt.savefig('activity.png')
  #plt.show() 
  plt.savefig(img_data, format='png')
  img_data.seek(0)
  # put plot in S3 bucket
  bucket = boto3.resource('s3').Bucket('mycalactivity')
  bucket.put_object(Body=img_data, ContentType='image/png', Key='activity.png')

  #generate presigned url
  url = s3.generate_presigned_url('get_object', 
      Params={'Bucket': 'mycalactivity', 'Key': 'activity.png'},
      ExpiresIn=86400)
  print(url)
  bot.send_photo(chat_id='582942300', photo=url)
  return url

def response(myhtml):
    return {
        "statusCode": 200,
        "body": myhtml,
        "headers": {
            "Content-Type": "text/html",
        }
    }
  

def lambda_handler(event, context):
    try: 
        fromDate = str(event.get('queryStringParameters')['fromDate'])
        toDate = str(event.get('queryStringParameters')['toDate'])
    except Exception as e:
        fromDate = str(date.today()- timedelta(days = 2))
        toDate = str(date.today())
        
    robj = weekly_bar_chart(fromDate,toDate)
    return response('<html><head><title>Weekly Activity</title></head>' + 
        '<body><div><img src=' + robj + ' alt="Image" width="750" height="600"></body></html>')
