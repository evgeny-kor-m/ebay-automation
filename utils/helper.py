import logging
import os
import random
import shutil
from typing import cast
import csv
import json


from datetime import datetime

class util:

    def __init__(self):  pass

    def GUID(self):
        guid= ""
        szTemp = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
        szHex = "0123456789abcdef-"
        nLen = len(szTemp)

        for num in range(0, nLen):
            r = random.randint(0, 100) % 16
            c = ' '

            match (szTemp[num]):
                case 'x':
                    c = szHex[r]
                case 'y':
                    c = szHex[r & 0x03 | 0x08]
                case '-':
                    c = '-'
                case '4':
                    c = '4'

            c = c if num < nLen else '0'
            guid = guid[:num] + c + guid[num+1:]

        print(datetime.now().strftime('(%Y-%m-%d %H:%M:%S)') , " Generated GUID:", guid)
        return guid
    @staticmethod
    def sortStr(source) -> str:
        i=0
        j=i+1
        tmp=0
        small_char=''
        try:
            while i < len(source) :
                while(j<len(source)):
                    if(source[tmp]>source[j]):
                        tmp=j
                    j+=1
                if i != tmp:
                    small_char = source[tmp]
                    source = source[:tmp] + source[i] + source[tmp+1:]
                    source = source[:i] + small_char + source[i+1:]
                i+=1
                j=i+1
        except Exception as e:
            print(f"An error occurred: {e}")
        return source
    @staticmethod
    def replaceStr(source,target, new )-> str:
        try:
            i=j=start=i_save=0
            while( i < len(source)):
                while(j < len(target) and source[i]==target[j]):
                    if(start==0):
                        start=1
                        i_save=i
                    i+=1
                    j+=1
                if(j==len(target)):
                    j=0
                    i=i_save
                    while(j<len(target)):
                        source = source[:i] + new[j] + source[i+1:]
                        i+=1
                        j+=1
                if(start==1):
                    start=0
                    i=i_save
                    j=0
                i+=1
        except Exception as e:
            print(f"An error occurred: {e}")
        return source
    @staticmethod
    def calcListItems(content):
        datalist=content.split(" ")
        dataDict = {}
        for listItem in datalist:
            if listItem in dataDict:
                dataDict[listItem]+=1
            else:
                dataDict[listItem]=1
        return dataDict

class file():
    def __init__(self):  pass
    
    def move_folder_contents(source_dir, target_dir):
        
        """
        Moves all contents from the source directory to the target directory.
        """
        source_dir = os.path.abspath(source_dir)
        target_dir = os.path.abspath(target_dir)

        # Check if source directory exists
        if not os.path.exists(source_dir):
            print(f"Source directory not found: {source_dir}")
            return

        # Create target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"Created target directory: {target_dir}")

        items = os.listdir(source_dir)
        
        # Check if directory is empty
        if not items:
            print("Source directory is empty.")
            return

        for item in items:
            if item.startswith("RUN_"): continue
            source_path = os.path.join(source_dir, item)
            target_path = os.path.join(target_dir, item)
            if source_path == target_dir: continue

            try:
                # Check for collisions
                if os.path.exists(target_path):
                    print(f"Item already exists and will be skipped: {item}")
                    continue

                # Move the item
                shutil.move(source_path, target_path)
                print(f"Successfully moved: {item}")
                
            except Exception as e:
                print(f"Failed to move {item}: {e}")

    @staticmethod
    def writeToFile( path, content) -> None:
        try:
            if not os.path.exists(path):
                with open(path, "w") as file:
                    file.write(content)
                    file.write("\n")
            else:
                with open(path, "a") as file:
                    file.write(content)
                    file.write("\n")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            file.close()
    
    @staticmethod
    def readFile(path) -> str :
        with open(path, 'r') as file:
            content = file.read()
        return content
    
    @staticmethod
    def readListLines(path) -> list:
        with open(path, 'r') as file:
            lines = file.readlines()
        return lines
    
    @staticmethod
    def readCvsFile(path) :
        with open(path, 'r') as file:
            csv_reader = csv.reader(file)
            # for row in csv_reader:
            #     print(row)  # Each row is a list
        return csv_reader
    
    @staticmethod
    def readJsonFile(path):
        with open(path, 'r') as file:
            data = json.load(file)  # Converts JSON to Python dictionary
        return data
    
    @staticmethod
    def writeJsonFile(path,content):
        # Save JSON data to file
        try:
            with open(path, "w",encoding="utf-8") as json_file:
                json.dump(content,  json_file ,indent=4)
        except Exception as e:
            print(f"An error occurred: {e}")

class Jason_util:
    @staticmethod
    def find_value(data, target):
        if isinstance(data, dict):
            for key, value in data.items():
                if value == target:
                    return key, value
                elif isinstance(value, (dict, list)):
                    result = Jason_util.find_value(value, target)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = Jason_util.find_value(item, target)
                if result:
                    return result
        return None

    @classmethod
    def update_value(cls,data, key, target_value, new_value):
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key and v == target_value:
                    data[k] = new_value
                elif isinstance(v, (dict, list)):
                    cls.update_value(v, key, target_value, new_value)
        elif isinstance(data, list):
            for item in data:
                cls.update_value(item, key, target_value, new_value)
