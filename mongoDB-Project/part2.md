
Part 2: Queries on the data in mongodb.


1.	db.yelp.business.find({$or: [{"full_address" : {$regex : ".*89117.*"}},{"full_address" : {$regex : ".*89122.*"}}]}).count()

2.	db.yelp.business.find({"full_address": {$regex: ".*Las Vegas.*"}}).count()

3.	 db.yelp.business.find({ "loc" : { $geoWithin : { $centerSphere: [ [ -80.839186, 35.226504 ], 5 / 3963.2 ] } } }).count()

4.	db.yelp.review.find({"_id" : ObjectId("581a51abbd45e57b60ae9203")}).count()

5.	db.yelp.review.find({ $and : [{"_id" : ObjectId("P1fJb2WQ1mXoiudj8UE44w")}, {"stars" : 5}]}).count()

6.	db.yelp.user.find({ "yelping_since" : {$lte:"2011-11"}}).count()

7.  db.yelp.tip.find().sort({"likes":-1}).limit(3)

8.	db.yelp.user.aggregate([{$group:{_id:"review_count",averageReviewCount:{$avg:"$review_count"}}}])

9.	db.yelp.user.find({"elite":{"$ne":[]}},{"_id":0,"user_id":1,"name":1,"elite":1})

10.	db.yelp.user.aggregate( [{ $unwind : "$elite" },{ $group : { _id : "$_id", maxEliteYears : { $sum : 1 }} },{ $sort : { maxEliteYears : -1 } },{ $limit : 13 }] );

11.db.yelp.user.aggregate({$project: {elitelength:{$size:"$elite"}}},{$group:{_id:0, avg:{$avg:"$elitelength"}}})

11.db.yelp.user.aggregate( [{ $unwind : "$elite" },{ $group : { _id : "$_id", maxElite : { $sum : 1 }}},{$group:{_id:0,avg:{$avg:"$maxElite"}}}])

****************** DIFFICULT QUERY *************************

1.db.yelp.review.aggregate([{$lookup:{from:"yelp.business",localField:"business_id",foreignField: "city",as:"users_from_city"}])

2.db.yelp.checkin.aggregate([{$group:{_id: "$business_id",maxTotalAmount: { $max: "$checkin_info"}}}])

3.db.yelp.checkin.find({"checkin_info":{"$gt":17-5}},{"_id":0,"business_id":1}).pretty()

4.db.yelp.review.aggregate([{$match:{business_id:"mVHrayjG3uZ_RLHkLj-AMg"}},{$group:{_id:'$stars', count:{$sum:1}}}])

5.db.yelp.review.aggregate([{$group:{_id: "$business_id", avgstar:{$avg:"$stars"}}},{$match: {avgstar:{$gt:3.5}}}])
