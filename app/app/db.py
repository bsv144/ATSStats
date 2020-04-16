import os
import psycopg2
import json
from psycopg2.extensions import AsIs 
from psycopg2 import sql
from dotenv import load_dotenv
import pandas as pd
import datetime

#Загружаем переменные среды с файла
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

HOST     = os.environ.get('HOST')
PORT     = os.environ.get('PORT')
DBNAME   = os.environ.get('DBNAME')
USER     = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')

#Получаем пользователей групп
def get_ACDQueuesMembers():
	con_Monitoring = psycopg2.connect( dbname= 'Cx_Monitoring', user= USER, password= PASSWORD, host= HOST, port= PORT)
	con_Security = psycopg2.connect( dbname= 'Cx_Security', user= USER, password= PASSWORD, host= HOST, port= PORT)

	sq_Users = pd.read_sql_query(
		'''
		select * from public."U_Users"
		'''
	, con_Security)
	sq_ACDQueuesMembers = pd.read_sql_query(
		'''
		--IDUSerState - Статус номера
		---300 - ОнЛайн
		---302 - Отошёл
		---301 - Перерыв
		---399 - Не подключен

		-- ExtensionState - Состояние номера
		--- 1 - Свободен
		--- 2 - Занят
		select macq."IDUser", mua."ExtensionState", mua."IDUserState",
			case
				when macq."IDACD" in (5000049053,5014640991) then 'Колл-Центр (61-02-05)'
				when macq."IDACD" = 5014846675 then 'Приём показаний (61-05-25)'
			end as "Name"
		from "M_ACDQueuesMembers" as macq
		join "M_UsersStates" as mua on macq."IDUser" = mua."IDUser"
		where macq."IDACD" in (5000049053,5014846675,5014640991)
		and mua."IDUserState" != 399
		order by macq."IDACD"
		'''
	, con_Monitoring)
	con_Monitoring.close()
	con_Security.close()

	df_Users = pd.DataFrame(sq_Users)
	df_ACDQueuesMembers = pd.DataFrame(sq_ACDQueuesMembers)
	result = pd.merge(df_ACDQueuesMembers, df_Users, how='left', left_on='IDUser', right_on='ID')
	#print( result )
	result_groups = result.groupby('Name')
	#Создаём словарь с данными для дальнейшего вывода в формате json
	json_out = {"CallGroups" : []}
	for name, group in result_groups:
		json_out["CallGroups"].append({"groupname" : name, "members" : group.to_json(orient='records')})
	json_out = json.dumps(json_out)
	return json_out

#Получаем статистику 
def get_StatisticsByCall():
	con_Statistics = psycopg2.connect( dbname= 'Cx_Statistics', user= USER, password= PASSWORD, host= HOST, port= PORT)
	con_Statistics.set_client_encoding('UTF8')
	odt = datetime.datetime.today().strftime("%Y-%m-%d")
	sq_Statistics = pd.read_sql_query(
		f'''
		WITH stats_seancescount AS  (
			--Кол-во принятых звонков
			select  "ANumberDialed",
				sum("Общее кол-во звонков") as "Общее кол-во звонков",
				sum("Обработано первым оператором") as "Обработано первым оператором",
				sum("Обработано в IVR") as "Обработано в IVR",
				sum("Обработано оператором") as "Обработано оператором",
				sum("Потеряно во  время ожидания") as "Потеряно во  время ожидания"
			from (
				select "ANumberDialed",
					count("ANumberDialed") as "Общее кол-во звонков",
					case
					when "SeanceResult" = 101 then count("SeanceResult")
					end as "Обработано первым оператором",
					case
					when "SeanceResult" = 114 then count("SeanceResult")
					end as "Обработано в IVR",
					case
					when "SeanceResult" = 102 then count("SeanceResult")
					end as "Обработано оператором",
					case
					when "SeanceResult" = 191 then count("SeanceResult")
					end as "Потеряно во  время ожидания"
				from public."S_Seances"
				WHERE "TimeStartDate" = '{odt}'
				--Входящие звонки
				and "SeanceType" = 1
				GROUP BY "ANumberDialed","SeanceResult"
			) as t1
			GROUP BY "ANumberDialed"
		), stats_durationcalls as (
			--Среднее время обработки звонка
			select "ANumberDialed",
				avg("DurationWait") as "Время ожидания", 
				avg("DurationTalk") as "Время разговора"
			from public."S_Seances"
			WHERE "TimeStartDate" = '{odt}'
				--Входящие звонки
				and "SeanceType" = 1
				--Данную статистику берём только для звонков обработанных первым опертором и оператором
				and "SeanceResult" in (101,102)
			GROUP BY "ANumberDialed"
		)

		select 
			case
				when ss."ANumberDialed" = '79227810205' then 'Колл-Центр (61-02-05)'
				when ss."ANumberDialed" = '79324080525' then 'Приём показаний (61-05-25)'
			end as "ANumberDialed",
			COALESCE("Общее кол-во звонков",0) as "Общее кол-во звонков", 
			COALESCE("Обработано первым оператором",0) as "Обработано первым оператором",
			COALESCE("Обработано в IVR",0) as "Обработано в IVR",
			COALESCE("Обработано оператором",0) as "Обработано оператором", 
			COALESCE("Потеряно во  время ожидания",0) as "Потеряно во  время ожидания",
			COALESCE("Время ожидания",0) as "Время ожидания",
			COALESCE("Время разговора",0) as "Время разговора"
		from stats_seancescount as ss
		left join stats_durationcalls as sd on ss."ANumberDialed" = sd."ANumberDialed"	
		where ss."ANumberDialed" in ('79227810205', '79324080525')
		'''
	, con_Statistics)
	con_Statistics.close()
	df_Statistics = pd.DataFrame(sq_Statistics)
	#print(df_Statistics.to_json(orient='records'))
	json_out = df_Statistics.to_json(orient='records')
	# result_groups = df_Statistics.groupby('ANumberDialed')
	# #Создаём словарь с данными для дальнейшего вывода в формате json
	# json_out = {"StatsGroups" : []}
	# for name, group in result_groups:
	# 	json_out["StatsGroups"].append({"groupname" : name, "members" : group.to_json(orient='records')})
	json_out = json.dumps(json_out)
	# print(json_out)
	return json_out

#Получаем мониторинг по текущей очереди
def get_QueuesByCall():
	con_Monitoring = psycopg2.connect( dbname= 'Cx_Monitoring', user= USER, password= PASSWORD, host= HOST, port= PORT)
	con_Monitoring.set_client_encoding('UTF8')
	sq_Monitoring = pd.read_sql_query(
		'''
		WITH mAll as (
			SELECT "ANumberDialed", count("ANumberDialed") as "Кол-во в очереди"
			FROM public."M_Seances" as sen
			WHERE sen."ANumberDialed" in ('79227810205','79324080525')
				and "SeanceType" = 1
				and "SeanceState" <> 100
			GROUP BY "ANumberDialed"
		), mOperator as (
			SELECT "ANumberDialed", count("ANumberDialed") as "Очередь Оператор"
			FROM public."M_Seances" as sen
			WHERE sen."ANumberDialed" in ('79227810205','79324080525')
				and "SeanceType" = 1
				and "SeanceState" <> 100
				and "IVRDTMF" is null
			GROUP BY "ANumberDialed"
		), mIvr as (
			SELECT "ANumberDialed", count("ANumberDialed") as "Очередь IVR"
			FROM public."M_Seances" as sen
			WHERE sen."ANumberDialed" in ('79227810205','79324080525')
				and "SeanceType" = 1
				and "SeanceState" <> 100
				and ("IVRDTMF" != '' or  "IVRDTMF" is not null)
			GROUP BY "ANumberDialed"
		)

		select 	case
				when ma."ANumberDialed" = '79227810205' then 'Колл-Центр (61-02-05)'
				when ma."ANumberDialed" = '79324080525' then 'Приём показаний (61-05-25)'
			end as "ANumberDialed",
			COALESCE(ma."Кол-во в очереди",0) as "Кол-во в очереди",
			COALESCE(mo."Очередь Оператор",0) as "Очередь Оператор",
			COALESCE(mi."Очередь IVR",0) as "Очередь IVR"
		from mAll as ma
		left join mOperator as mo on ma."ANumberDialed" = mo."ANumberDialed"
		left join mIvr as mi on ma."ANumberDialed" = mi."ANumberDialed"
		'''
	, con_Monitoring)
	con_Monitoring.close()
	df_Monitoring = pd.DataFrame(sq_Monitoring)
	#print(df_Statistics.to_json(orient='records'))
	json_out = df_Monitoring.to_json(orient='records')
	# result_groups = df_Statistics.groupby('ANumberDialed')
	# #Создаём словарь с данными для дальнейшего вывода в формате json
	# json_out = {"StatsGroups" : []}
	# for name, group in result_groups:
	# 	json_out["StatsGroups"].append({"groupname" : name, "members" : group.to_json(orient='records')})
	json_out = json.dumps(json_out)
	# print(json_out)
	return json_out

