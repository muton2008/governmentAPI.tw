# -*- coding: utf-8 -*-
import requests
import json
import time

def cache(minutes): #decorate get()
    def decorator(func):
        cache.__dict__[func.__qualname__.split('.')[0]]={} #init dict
        def wrapper(*args, **kwargs):
            if not bool(cache.__dict__[func.__qualname__.split('.')[0]]) or time.time()//(minutes*60)!=cache.__dict__[func.__qualname__.split('.')[0]]["update_time"]: #if has cache and over timeout
                cache.__dict__[func.__qualname__.split('.')[0]]["update_time"]=time.time()//(minutes*60)
                cache.__dict__[func.__qualname__.split('.')[0]]["data"] = func(*args, **kwargs) #requests data
            return cache.__dict__[func.__qualname__.split('.')[0]]["data"]
        return wrapper
    return decorator

class electricity:
    """
    Real-time information on the power generation of each unit of Taipower's own and purchased power (including hydropower, thermal power, renewable energy, nuclear energy, etc.)
    """
    @cache(10)
    def get(self):
        """
        Return:
            type:dict
            content:{update_time,unprocessed generator data}
        """
        response=requests.get("https://service.taipower.com.tw/data/opendata/apply/file/d006001/001.json")
        response.raise_for_status()
        json_data = response.content.decode('utf-8-sig')  # 使用 utf-8-sig 解碼 JSON 字串
        return json.loads(json_data)
    
    def update_time(self):
        """
        Return:
            type:str
            content:YYYY-MM-DD hh-mm
        """
        data=self.get()
        return data[""]
    
    def filter_type(self,kind):
        """
        Parameters
        ----------
        kind(str):
            should be one of generator_type's return
            should be either '核能' or '燃煤' or '汽電共生' or '燃氣' or '燃油' or '輕油' or '水力' or '風力' or '太陽能' or '其他再生能源' or '儲能' or '儲能附載' or '民營電廠'
    
        ----------
        Return: 
            type:list
            content:[unit name, device capacity (MW), net power generation (MW), net power generation/device capacity ratio (%), remarks]
    
        """
        data=self.get()
        if kind!="all":
            data=[i for i in data["aaData"] if kind in i[0]]
        else:
            data=[i for i in data["aaData"]]
        return data
    
    def filter_unitName(self,name):
        """
        Parameters
        ----------
        name(str):
            shoul be one of generator_name's return
        ----------
        Return:
            type:list
            content:[generator type,unit name,device capacity (MW), net power generation (MW), net power generation/device capacity ratio (%), remarks]
        """
        data=self.get()
        return [j for i in data["aaData"] if i[1]==name for j in i ]
        
    
    def generator_rate(self,kind):
        """
        Parameters
        ----------
        kind(str):
            should be one of generator_type's return
            should be either '核能' or '燃煤' or '汽電共生' or '燃氣' or '燃油' or '輕油' or '水力' or '風力' or '太陽能' or '其他再生能源' or '儲能' or '儲能附載' or '民營電廠'
    
        ----------
        Return:
            type:list/dict
            content:[device capacity (MW),net power generation (MW)]
        """
        data=self.get()
        for i in data["aaData"]:
            if i[0]==kind and i[1]=="小計":
                return i[2:4]
        
    def generator_name(self):
        """
        Return:
            type:list
            content:[all unit names]
        """
        data=self.get()
        return [i[1] for i in data["aaData"]]
    
    def generator_type(self):
        """
        Return:
            type:list
            content:[Various types of generators]
        """
        data=self.get()
        return list(set([i[0] for i in data["aaData"]]))
        
class air_pollution:
    """
    Air quality indicators at each measuring station(AQI)
    """
    @cache(60)
    def get(self): #60min update
        """
        Return:
            type:dict
            content:{Data statement,data information,unprocessed air data}
        """
        response=requests.get("https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON")
        response.raise_for_status()
        return response.json()
    
    def organize_records(self):
        """
        Return:
            type:dict
            content:{sitename:[all of the label and value of station]}
        """
        temp=self.get()["records"]
        data={}
        for i in temp:
            name=i["sitename"]
            del i["sitename"]
            data[name]=i
            
        return data
    
    def update_time(self):
        """
        Return:
            type:str
            content:YYYY-MM-DD hh-mm
        """
        data=self.get()
        return data["records"][0]["publishtime"]
    
    def identification(self):
        """
        Return:
            type:list
            content:[all the id in records]
        """
        data=self.get()
        return list(data["records"][0].keys())
    
    def declare(self,Identification):
        """
        Parameters
        ----------
        label(str):
            should be one of label's return 
        ----------
        Return:
            type:list
            content:[id's information]
        """
        data=self.get()
        return [i for i in data["fields"] if i["id"]==Identification][0]
    
    def sitename(self):
        """
        Return:
            type:list
            content:[all stations' name]
        """
        data=self.get()
        return [i["sitename"] for i in data["records"]]
    
    def county(self):
        """
        Return:
            type:set
            content:[all county in Taiwan]
        
        """
        data=self.get()
        return set([i["county"] for i in data["records"]])
    
    def sitename_of_county(self,city):
        """
        Parameters
        ----------
        city(str):
            should be one of county's return
        ----------
        Return:
            type:list
            content:[all of the station in city]
        """
        data=self.get()
        return [i["sitename"] for i in data["records"] if i["county"]==city]
    
    def filter_sitename(self,sitename):
        """
        Parameters
        ----------
        sitename(str):
            should be one of sitename's return
        ----------
        Return:
            type:dict
            content:{all of the label and value of station}
        """
        data=self.organize_records()
        
        return data[sitename]
    
    def filter_aqi(self,value,conds):
        """
        Parameters
        ----------
        value(int):
            the limit value of AQI
            
        conds(str):
            should be either '==' or '>' or '<' or '>=' or '<='
        ----------
        Return:
            type:list
            content:[Eligible site names]
        """
        if conds not in [">", "<", ">=", "<=", "=="]:
            raise ValueError("Invalid comparison operator")
        data=self.get()
        for j in range(len(data["records"])):
            if data["records"][j]["aqi"]=="":
                data["records"][j]["aqi"]="0"
        return eval(f'[i["sitename"] for i in data["records"] if int(i["aqi"]) {conds} {value}]')
    
    def filter_pollutant(self,pollutant,value,conds):
        """
        Parameters
        ----------
        pollutant(str):
            shold be either 'so2' or 'co' or 'o3' or 'o3_8hr' or 'pm10' or 'pm2.5' or 'no2' or 'nox' or 'no' or 'co_8hr' or 'pm2.5_avg' or 'pm10_avg' or 'so2_avg'
        value(float):
            the limit value of pollutant concentration
        conds(str):
            should be either '==' or '>' or '<' or '>=' or '<='
        ----------
        Return:
            type:list
            content:[Eligible site names]
        """
        if pollutant not in ('so2', 'co', 'o3', 'o3_8hr', 'pm10', 'pm2.5', 'no2', 'nox', 'no','co_8hr', 'pm2.5_avg', 'pm10_avg', 'so2_avg'):
            raise ValueError("pollutant are illegal")
        if conds not in [">", "<", ">=", "<=", "=="]:
            raise ValueError("Invalid comparison operator")
            
        data=self.get()
        for j in range(len(data["records"])):
            if data["records"][j][pollutant]=="":
                data["records"][j][pollutant]="0"
                
        return eval(f'[i["sitename"] for i in data["records"] if float(i["{pollutant}"]) {conds} {value}]')
    
    def wind_info(self,sitename):
        """
        Parameters
        ----------
        sitename(str):
            should be one of sitename's return
        ----------
        Return:
            type:list
            content:[wind_speed(m/sec),wind_direc]
        """
        data=self.get()
        return [[i["wind_speed"],i["wind_direc"]] for i in data["records"] if i["sitename"]==sitename][0]
    
    def station_coordinates(self,sitename):
        """
        Parameters
        ----------
        sitename(str):
            should be one of sitename's return 
        ----------
        Return:
            type:list
            content:[longitude,latitude]
        """
        data=self.organize_records()
        return [data[sitename]["longitude"],data[sitename]["latitude"]]
    
