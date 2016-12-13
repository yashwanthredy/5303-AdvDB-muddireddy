

from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask_restful import reqparse
from flask import jsonify
from flask_cors import CORS, cross_origin


#from pymongo import MongoClient
import pymongo
from bson import Binary, Code
from bson.json_util import dumps
from bson.objectid import ObjectId
#from pymongo import Connection, GEO2D

import datetime

import json
import urllib


import timeit

app = FlaskAPI(__name__)
CORS(app)

client = pymongo.MongoClient('localhost', 27017)

# change the following to fit your database configuration

db = client['test']   
businessdb = db['yelp.business']
reviewdb= db['yelp.review']
userdb = db['yelp.user']
testdb = db['yelp.test']
tipsdb = db['yelp.tip']



parser = reqparse.RequestParser()

# ROUTES
"""=================================================================================="""
"""=================================================================================="""
"""=================================================================================="""


@cross_origin() # allow all origins all methods.
@app.route("/", methods=['GET'])
def index():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return func_list

"""====================================="""
@app.route("/zip/<args>",methods=['GET'])
def zip(args):
    args=myParseArgs(args)
     
    data = []
    zips=args['zips']
    zip1,zip2 = zips.split(",")
    
    
    result = businessdb.find({},{'full_address':1,'_id':0})
    	
    for r in result:
        parts = r['full_address'].split(' ')
        target = parts[-1]
        if len(target) == 5 and target == zip1:
            data.append(r['full_address'])
        if len(target) == 5 and target == zip2:
            data.append(r['full_address'])
    if 'limit' in args.keys():
    	limit=int(args['limit'])
        return {"data":data[:limit]}
    else:
    	return {"data":data}
     
"""=================================================================================="""

@app.route("/city/<args>",methods=['GET'])
def city(args):
    args=myParseArgs(args)
    data = []
    city=args['city']
    result = businessdb.find({"full_address": {$regex: 'Las Vegas'}})
    count=0
    for r in result:
        if r['city'] == city:
            data.append(r['name'])
            count+=1
    if 'limit' in args.keys():
    	limit=int(args['limit'])
        return {"data":data[:limit]}
    else:
    	return {"data":data}
     
"""=================================================================================="""
@app.route("/closest/<args>",methods=['GET'])
def closest(args):
    args=myParseArgs(args)
    data = []
    lat=float(args['lat'])
    lon=float(args['lon'])
    
    rad=5/3963.2
    result = businessdb.find({"loc":{ '$geoWithin' : { '$center': [[lon,lat],rad]}}},{'_id':0,'name':1})
    count=0
    for r in result:
        data.append(r['name'])
       
    if 'limit' in args.keys():
    	limit=int(args['limit'])
        return {"data":data[:limit]}
    else:
    	return {"data":data}
     
"""=================================================================================="""
@app.route("/reviews/<args>",methods=['GET'])
def reviews(args):
    args=myParseArgs(args)
    data = []
    id=args['id']
    
    result = reviewdb.find({"business_id":id},{'_id':0})
    count=0
    for r in result:
        data.append(r)
       
    if 'limit' in args.keys():
    	limit=int(args['limit'])
        return {"data":data[:limit]}
    else:
    	return {"data":data}
     
"""=================================================================================="""
@app.route("/stars/<args>",methods=['GET'])
def stars(args):
    args=myParseArgs(args)
    data = []
    id=args['id']
    num_stars=int(args['num_stars'])
    
    result = reviewdb.find({ '$and' : [{'business_id' : id}, {'stars' :num_stars}]},{'_id':0})
    count=0
    for r in result:
        data.append(r)
       
    if 'limit' in args.keys():
    	limit=int(args['limit'])
        return {"data":data[:limit]}
    else:
    	return {"data":data}
     
"""=================================================================================="""
@app.route("/yelping/<args>",methods=['GET'])
def yelping(args):
    args=myParseArgs(args)
    myyear = datetime.datetime.today().year
    mymonth= datetime.datetime.today().month
    ans = []
    years=int(args['min_years'])
    limit=int(args['limit'])
    myy=myyear-years
    min_years = str(str(myy) + '-' + str(mymonth))
    result =userdb.find({ "yelping_since" : {'$lte':min_years}},{"_id":None,"name":1,"yelping_since":1}).limit(limit)
    for r in result:
        ans.append(r)
    if 'limit' in args.keys():
        return {"data":ans[:limit]}
    else:
    	return {"data":ans}
     
"""=================================================================================="""
@app.route("/most_likes/<args>",methods=['GET'])
def most_likes(args):
    args=myParseArgs(args)
    ans = []
    limit=int(args['limit'])
    result =tipsdb.find({},{"_id" : 0}).sort([('likes' , -1)]).limit(limit)
    count=0
    for r in result:
        ans.append(r)
   
    return {"data":ans}
     
"""=================================================================================="""
@app.route("/review_count/",methods=['GET'])
def review_count():
    ans = []
    result =userdb.aggregate([{'$group':{"_id":"review_count",'averageReviewCount':{'$avg':"$review_count"}}}])
    count=0
    for r in result:
        ans.append(r)
    return {"data":ans}
     
"""=================================================================================="""
@app.route("/elite/<args>",methods=['GET'])
def elite(args):
    args=myParseArgs(args)
    ans = []
    
    if 'sorted' in args.keys():
        result=userdb.aggregate( [{ '$unwind' : "$elite" },{ '$group' : { '_id':0 ,'maxEliteYears' : { '$sum' : 1 }} },{ '$sort' : { 'maxEliteYears' : -1 } }] )
    else:
        result =userdb.find({"elite":{"$ne":[]}},{"_id":0,"user_id":1,"name":1,"elite":1})
    count=0
    for r in result:
        ans.append(r)
    if 'limit' in args.keys():
    	limit=int(args['limit'])
        return {"data":ans[:limit]}
    else:
    	return {"data":ans}
     
"""=================================================================================="""
@app.route("/avg_elite/",methods=['GET'])
def avg_elite():
    ans = []
    result =userdb.aggregate( [{ '$unwind' : "$elite" },{ '$group' : { '_id' : "$_id",'maxElite' : { '$sum' : 1 }}},{'$group':{"_id":None,'avg':{'$avg':"$maxElite"}}}])
    count=0
    for r in result:
        ans.append(r)
    return {"data":ans}
     
"""=================================================================================="""

@app.route("/user/<args>", methods=['GET'])
def user(args):

    args = myParseArgs(args)
    
    if 'skip' in args.keys():
        args['skip'] = int(args['skip'])
    if 'limit' in args.keys():
        args['limit'] = int(args['limit'])

    data = []
    
    #.skip(1).limit(1)
    
    if 'skip' in args.keys() and 'limit' in args.keys():
        result = userdb.find({},{'_id':0}).skip(args['skip']).limit(args['limit'])
    elif 'skip' in args.keys():
        result = userdb.find({},{'_id':0}).skip(args['skip'])
    elif 'limit' in args.keys():
        result = userdb.find({},{'_id':0}).limit(args['limit'])
    else:
        result = userdb.find({},{'_id':0}).limit(10)  

    for row in result:
        data.append(row)
    return {"data":data}
    
"""=================================================================================="""
@app.route("/test/", methods=['POST'])
def test():
    
    data = request.data
    #testdb.insert(request)
    
    return data

@app.route("/<int:key>/", methods=['POST'])
def findkey(key):
    
    data = request.data
    data['key'] = key
    #testdb.insert(request)
    
    return data
    
"""=================================================================================="""
@app.route("/business/<args>", methods=['GET'])
def business(args):

    args = myParseArgs(args)
    
    data = []
    
    result = businessdb.find({},{'_id':0}).limit(100)
    
    for row in result:
        data.append(row)
    

    return {"data":data}
    
# HELPER METHODS
"""=================================================================================="""
"""=================================================================================="""
"""=================================================================================="""

def snap_time(time,snap_val):
    time = int(time)
    m = time % snap_val
    if m < (snap_val // 2):
        time -= m
    else:
        time += (snap_val - m)
        
    if (time + 40) % 100 == 0:
        time += 40
        
    return int(time)

"""=================================================================================="""
def myParseArgs(pairs=None):
    """Parses a url for key value pairs. Not very RESTful.
    Splits on ":"'s first, then "=" signs.
    
    Args:
        pairs: string of key value pairs
        
    Example:
    
        curl -X GET http://cs.mwsu.edu:5000/images/
        
    Returns:
        json object with all images
    """
    
    if not pairs:
        return {}
    
    argsList = pairs.split(":")
    argsDict = {}

    for arg in argsList:
        key,val = arg.split("=")
        argsDict[key]=str(val)
        
    return argsDict

    

if __name__ == "__main__":
    app.run(debug=True,host='67.205.136.186',port=5000)
